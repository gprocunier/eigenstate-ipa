import copy
import datetime
import importlib.util
import pathlib
import sys
import types
import unittest

from unittest import mock

from tests.error_helpers import exception_text

COLLECTION_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _fake_ipalib():
    fake_not_found = type('NotFound', (Exception,), {})
    fake_auth_error = type('AuthorizationError', (Exception,), {})
    fake_aci_error = type('ACIError', (Exception,), {})
    fake_empty_modlist = type('EmptyModlist', (Exception,), {})

    fake_errors = types.SimpleNamespace(
        NotFound=fake_not_found,
        AuthorizationError=fake_auth_error,
        ACIError=fake_aci_error,
        EmptyModlist=fake_empty_modlist,
    )

    fake_api = types.SimpleNamespace(
        isdone=lambda _state: True,
        bootstrap=lambda **kwargs: None,
        finalize=lambda: None,
        Backend=types.SimpleNamespace(
            rpcclient=types.SimpleNamespace(
                isconnected=lambda: True,
                connect=lambda ccache=None: None,
            )
        ),
        Command=types.SimpleNamespace(),
    )

    fake_ipalib_mod = types.ModuleType('ipalib')
    fake_ipalib_mod.api = fake_api
    fake_ipalib_mod.errors = fake_errors

    fake_install = types.ModuleType('ipalib.install')
    fake_install_kinit = types.ModuleType('ipalib.install.kinit')
    fake_install_kinit.kinit_password = lambda p, pw, cc: None
    fake_kinit = types.ModuleType('ipalib.kinit')
    fake_kinit.kinit_password = lambda p, pw, cc: None

    sys_patches = {
        'ipalib': fake_ipalib_mod,
        'ipalib.errors': fake_errors,
        'ipalib.install': fake_install,
        'ipalib.install.kinit': fake_install_kinit,
        'ipalib.kinit': fake_kinit,
    }
    return fake_ipalib_mod, fake_errors, fake_api, sys_patches


def _load_ipa_client(sys_patches):
    name = 'eigenstate_ipa_test_ipa_client_for_user_lease'
    path = COLLECTION_ROOT / 'plugins' / 'module_utils' / 'ipa_client.py'
    with mock.patch.dict(sys.modules, sys_patches, clear=False):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return mod


def _load_user_lease(sys_patches, ipa_client_mod):
    name = 'eigenstate_ipa_test_user_lease'
    path = COLLECTION_ROOT / 'plugins' / 'modules' / 'user_lease.py'

    collection_pkg = types.ModuleType(
        'ansible_collections.eigenstate.ipa.plugins.module_utils.ipa_client')
    collection_pkg.IPAClient = ipa_client_mod.IPAClient
    collection_pkg.IPAClientError = ipa_client_mod.IPAClientError

    extra_patches = {
        'ansible_collections': types.ModuleType('ansible_collections'),
        'ansible_collections.eigenstate': types.ModuleType('ansible_collections.eigenstate'),
        'ansible_collections.eigenstate.ipa': types.ModuleType('ansible_collections.eigenstate.ipa'),
        'ansible_collections.eigenstate.ipa.plugins': types.ModuleType('ansible_collections.eigenstate.ipa.plugins'),
        'ansible_collections.eigenstate.ipa.plugins.module_utils': types.ModuleType(
            'ansible_collections.eigenstate.ipa.plugins.module_utils'),
        'ansible_collections.eigenstate.ipa.plugins.module_utils.ipa_client': collection_pkg,
    }

    combined = dict(sys_patches)
    combined.update(extra_patches)

    with mock.patch.dict(sys.modules, combined, clear=False):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return mod


def _module_params(**overrides):
    params = dict(
        username='lease-target',
        state='present',
        principal_expiration='2026-04-09T18:30:00Z',
        password_expiration=None,
        password_expiration_matches_principal=True,
        clear_password_expiration=False,
        require_groups=[],
        server='idm-01.example.com',
        ipaadmin_principal='admin',
        ipaadmin_password='secret',
        kerberos_keytab=None,
        verify=None,
    )
    params.update(overrides)
    return params


def _make_module(params, check_mode=False):
    module = mock.MagicMock()
    module.params = params
    module.check_mode = check_mode
    module.warn = mock.MagicMock()
    captured = {}

    def exit_json(**kwargs):
        captured.update(kwargs)
        raise SystemExit(0)

    def fail_json(**kwargs):
        captured.update(kwargs)
        raise SystemExit(1)

    module.exit_json.side_effect = exit_json
    module.fail_json.side_effect = fail_json
    module._captured = captured
    return module


def _entry(uid='lease-target', principal=None, password=None, groups=None):
    record = {
        'uid': (uid,),
        'memberof_group': tuple(groups or []),
    }
    if principal is not None:
        record['krbprincipalexpiration'] = (principal,)
    if password is not None:
        record['krbpasswordexpiration'] = (password,)
    return record


class UserLeaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake_ipalib, cls.fake_errors, cls.fake_api, cls.sys_patches = _fake_ipalib()
        cls.ipa_client_mod = _load_ipa_client(cls.sys_patches)
        cls.mod = _load_user_lease(cls.sys_patches, cls.ipa_client_mod)
        cls.mod.ipalib_errors = cls.fake_errors
        cls.mod.HAS_IPALIB = True

    def _run(self, params, entry, check_mode=False):
        api = self.fake_api
        state = {'entry': copy.deepcopy(entry)}

        def user_show(username, all=True):
            if username != state['entry']['uid'][0]:
                raise self.fake_errors.NotFound('missing')
            return {'result': copy.deepcopy(state['entry'])}

        def user_mod(username, setattr=None, delattr=None, **kwargs):
            if username != state['entry']['uid'][0]:
                raise self.fake_errors.NotFound('missing')
            for item in setattr or []:
                attr, value = item.split('=', 1)
                state['entry'][attr] = (self.mod._as_utc_naive(value),)
            for item in delattr or []:
                attr, _sep, _value = item.partition('=')
                state['entry'].pop(attr, None)
            return {'result': copy.deepcopy(state['entry'])}

        api.Command = types.SimpleNamespace(
            user_show=user_show,
            user_mod=user_mod,
        )

        module_mock = _make_module(params, check_mode=check_mode)

        client_instance = mock.MagicMock()
        client_instance.connect = mock.MagicMock()
        client_instance.cleanup = mock.MagicMock()
        client_instance.api = api
        client_instance.errors = self.fake_errors

        real_cls = self.ipa_client_mod.IPAClient
        MockIPAClient = mock.MagicMock(spec=real_cls)
        MockIPAClient.authz_error_kind = real_cls.authz_error_kind
        MockIPAClient.is_authz_error = real_cls.is_authz_error
        MockIPAClient.authz_error_message = real_cls.authz_error_message
        MockIPAClient.return_value = client_instance

        with mock.patch.object(self.mod, 'AnsibleModule', return_value=module_mock):
            with mock.patch.object(self.mod, 'IPAClient', MockIPAClient):
                try:
                    self.mod.run_module()
                except SystemExit:
                    pass

        return module_mock._captured, state['entry']

    def test_parse_relative_hhmm(self):
        now = datetime.datetime(2026, 4, 8, 12, 0, 0)
        self.assertEqual(
            self.mod._parse_time_spec('02:30', now=now),
            datetime.datetime(2026, 4, 8, 14, 30, 0),
        )


    def test_sensitive_module_requires_explicit_tls_trust_or_opt_out(self):
        warnings = []
        client = self.ipa_client_mod.IPAClient(
            warn_callback=warnings.append,
            require_trusted_tls=True,
        )
        with mock.patch.object(self.ipa_client_mod.os.path, 'exists', return_value=False):
            with self.assertRaises(self.ipa_client_mod.IPAClientError) as ctx:
                client._resolve_verify(None)
        self.assertIn('verify', exception_text(ctx.exception))
        self.assertEqual(warnings, [])

    def test_present_sets_principal_and_password(self):
        params = _module_params()
        captured, entry = self._run(params, _entry(groups=['lease-targets']))
        self.assertTrue(captured['changed'])
        self.assertEqual(captured['principal_expiration_after'], '20260409183000Z')
        self.assertEqual(captured['password_expiration_after'], '20260409183000Z')
        self.assertEqual(entry['krbprincipalexpiration'][0], datetime.datetime(2026, 4, 9, 18, 30, 0))

    def test_missing_required_group_fails(self):
        params = _module_params(require_groups=['lease-targets'])
        captured, _entry_state = self._run(params, _entry(groups=['ipausers']))
        self.assertIn('missing required group membership', captured['msg'])
        self.assertEqual(captured['groups_missing'], ['lease-targets'])

    def test_cleared_uses_delattr(self):
        params = _module_params(
            state='cleared',
            principal_expiration=None,
            password_expiration_matches_principal=False,
            clear_password_expiration=True,
        )
        current = _entry(
            principal=datetime.datetime(2037, 4, 4, 18, 30, 40),
            password=datetime.datetime(2036, 4, 4, 18, 30, 40),
            groups=['lease-targets'],
        )
        captured, entry = self._run(params, current)
        self.assertTrue(captured['changed'])
        self.assertIsNone(captured['principal_expiration_after'])
        self.assertIsNone(captured['password_expiration_after'])
        self.assertNotIn('krbprincipalexpiration', entry)
        self.assertNotIn('krbpasswordexpiration', entry)

    def test_check_mode_preview_does_not_mutate_backend(self):
        params = _module_params(
            state='expired',
            principal_expiration=None,
            password_expiration_matches_principal=True,
        )
        before = _entry(groups=['lease-targets'])
        captured, entry = self._run(params, before, check_mode=True)
        self.assertTrue(captured['changed'])
        self.assertIsNotNone(captured['principal_expiration_after'])
        self.assertNotIn('krbprincipalexpiration', entry)

    def test_reports_authorization_failure_clearly(self):
        params = _module_params()

        api = self.fake_api
        state = {'entry': copy.deepcopy(_entry(groups=['lease-targets']))}

        def user_show(username, all=True):
            return {'result': copy.deepcopy(state['entry'])}

        def user_mod(username, setattr=None, delattr=None, **kwargs):
            raise self.fake_errors.AuthorizationError('denied')

        api.Command = types.SimpleNamespace(user_show=user_show, user_mod=user_mod)

        module_mock = _make_module(params)
        client_instance = mock.MagicMock()
        client_instance.connect = mock.MagicMock()
        client_instance.cleanup = mock.MagicMock()
        client_instance.api = api
        client_instance.errors = self.fake_errors

        real_cls = self.ipa_client_mod.IPAClient
        MockIPAClient = mock.MagicMock(spec=real_cls)
        MockIPAClient.authz_error_kind = real_cls.authz_error_kind
        MockIPAClient.is_authz_error = real_cls.is_authz_error
        MockIPAClient.authz_error_message = real_cls.authz_error_message
        MockIPAClient.return_value = client_instance

        with mock.patch.object(self.mod, 'AnsibleModule', return_value=module_mock):
            with mock.patch.object(self.mod, 'IPAClient', MockIPAClient):
                try:
                    self.mod.run_module()
                except SystemExit:
                    pass

        self.assertIn("Not authorized to modify lease attributes for user 'lease-target'", module_mock._captured['msg'])

    def test_reports_aci_failure_clearly(self):
        params = _module_params()

        api = self.fake_api
        state = {'entry': copy.deepcopy(_entry(groups=['lease-targets']))}

        def user_show(username, all=True):
            return {'result': copy.deepcopy(state['entry'])}

        def user_mod(username, setattr=None, delattr=None, **kwargs):
            raise self.fake_errors.ACIError('aci denied')

        api.Command = types.SimpleNamespace(user_show=user_show, user_mod=user_mod)

        module_mock = _make_module(params)
        client_instance = mock.MagicMock()
        client_instance.connect = mock.MagicMock()
        client_instance.cleanup = mock.MagicMock()
        client_instance.api = api
        client_instance.errors = self.fake_errors

        real_cls = self.ipa_client_mod.IPAClient
        MockIPAClient = mock.MagicMock(spec=real_cls)
        MockIPAClient.authz_error_kind = real_cls.authz_error_kind
        MockIPAClient.is_authz_error = real_cls.is_authz_error
        MockIPAClient.authz_error_message = real_cls.authz_error_message
        MockIPAClient.return_value = client_instance

        with mock.patch.object(self.mod, 'AnsibleModule', return_value=module_mock):
            with mock.patch.object(self.mod, 'IPAClient', MockIPAClient):
                try:
                    self.mod.run_module()
                except SystemExit:
                    pass

        self.assertIn("Access-control policy denied modify lease attributes for user 'lease-target'", module_mock._captured['msg'])

    def test_validation_requires_target_value_for_present(self):
        params = _module_params(
            principal_expiration=None,
            password_expiration=None,
        )
        captured, _entry_state = self._run(params, _entry())
        self.assertIn('state=present requires', captured['msg'])

    def test_validation_requires_principal_when_matching_password_to_principal(self):
        params = _module_params(
            principal_expiration=None,
            password_expiration='2026-04-09T19:00:00Z',
            password_expiration_matches_principal=True,
        )
        captured, _entry_state = self._run(params, _entry())
        self.assertIn('mutually exclusive', captured['msg'])

    def test_explicit_password_only_requires_unsafe_opt_out(self):
        params = _module_params(
            principal_expiration=None,
            password_expiration='2026-04-09T19:00:00Z',
            password_expiration_matches_principal=False,
        )
        captured, entry = self._run(params, _entry(groups=['lease-targets']))
        self.assertTrue(captured['changed'])
        self.assertIsNone(captured['principal_expiration_after'])
        self.assertEqual(captured['password_expiration_after'], '20260409190000Z')
        self.assertNotIn('krbprincipalexpiration', entry)


if __name__ == '__main__':
    unittest.main()
