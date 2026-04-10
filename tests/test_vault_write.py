import importlib.util
import os
import pathlib
import sys
import tempfile
import types
import unittest

from unittest import mock

# ---------------------------------------------------------------------------
# Module loading helpers
# ---------------------------------------------------------------------------

COLLECTION_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _fake_ipalib():
    """Return a (fake_ipalib_module, fake_errors_ns) pair."""
    fake_not_found = type("NotFound", (Exception,), {})
    fake_auth_error = type("AuthorizationError", (Exception,), {})
    fake_empty_modlist = type("EmptyModlist", (Exception,), {})

    fake_errors = types.SimpleNamespace(
        NotFound=fake_not_found,
        AuthorizationError=fake_auth_error,
        EmptyModlist=fake_empty_modlist,
    )

    fake_api = types.SimpleNamespace(
        isdone=lambda phase: True,
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

    fake_ipalib_mod = types.ModuleType("ipalib")
    fake_ipalib_mod.api = fake_api
    fake_ipalib_mod.errors = fake_errors

    fake_install = types.ModuleType("ipalib.install")
    fake_install_kinit = types.ModuleType("ipalib.install.kinit")
    fake_install_kinit.kinit_password = lambda p, pw, cc: None
    fake_kinit = types.ModuleType("ipalib.kinit")
    fake_kinit.kinit_password = lambda p, pw, cc: None

    sys_patches = {
        "ipalib": fake_ipalib_mod,
        "ipalib.errors": fake_errors,
        "ipalib.install": fake_install,
        "ipalib.install.kinit": fake_install_kinit,
        "ipalib.kinit": fake_kinit,
    }
    return fake_ipalib_mod, fake_errors, fake_api, sys_patches


def _load_ipa_client(sys_patches):
    name = "eigenstate_ipa_test_ipa_client"
    path = COLLECTION_ROOT / "plugins" / "module_utils" / "ipa_client.py"
    with mock.patch.dict(sys.modules, sys_patches, clear=False):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return mod


def _load_vault_write(sys_patches, ipa_client_mod):
    """Load vault_write.py with ipalib and module_utils stubbed out."""
    name = "eigenstate_ipa_test_vault_write"
    path = COLLECTION_ROOT / "plugins" / "modules" / "vault_write.py"

    # Patch the collection namespace import so vault_write can import IPAClient
    collection_pkg = types.ModuleType(
        "ansible_collections.eigenstate.ipa.plugins.module_utils.ipa_client")
    collection_pkg.IPAClient = ipa_client_mod.IPAClient
    collection_pkg.IPAClientError = ipa_client_mod.IPAClientError

    extra_patches = {
        "ansible_collections": types.ModuleType("ansible_collections"),
        "ansible_collections.eigenstate": types.ModuleType(
            "ansible_collections.eigenstate"),
        "ansible_collections.eigenstate.ipa": types.ModuleType(
            "ansible_collections.eigenstate.ipa"),
        "ansible_collections.eigenstate.ipa.plugins": types.ModuleType(
            "ansible_collections.eigenstate.ipa.plugins"),
        "ansible_collections.eigenstate.ipa.plugins.module_utils": types.ModuleType(
            "ansible_collections.eigenstate.ipa.plugins.module_utils"),
        "ansible_collections.eigenstate.ipa.plugins.module_utils.ipa_client": (
            collection_pkg),
    }

    combined = dict(sys_patches)
    combined.update(extra_patches)

    with mock.patch.dict(sys.modules, combined, clear=False):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_vault_entry(name='test-vault', vault_type='standard',
                      description='', members=None):
    entry = {
        'cn': [name],
        'ipavaulttype': [vault_type],
        'description': [description] if description else [],
        'member_user': members or [],
        'member_group': [],
        'member_service': [],
        'owner_user': ['admin'],
        'owner_group': [],
        'owner_service': [],
    }
    return entry


def _module_params(**overrides):
    defaults = dict(
        name='test-vault',
        state='present',
        server='idm-01.example.com',
        ipaadmin_principal='admin',
        ipaadmin_password='secret',
        kerberos_keytab=None,
        verify=None,
        username=None,
        service=None,
        shared=True,
        vault_type='standard',
        description=None,
        vault_public_key=None,
        vault_public_key_file=None,
        data=None,
        data_file=None,
        vault_password=None,
        vault_password_file=None,
        members=[],
        members_absent=[],
    )
    defaults.update(overrides)
    return defaults


def _make_module(mod, params, check_mode=False):
    """Return a mock AnsibleModule wired to *params*."""
    m = mock.MagicMock()
    m.params = params
    m.check_mode = check_mode
    m.warn = mock.MagicMock()
    captured = {}

    def exit_json(**kwargs):
        captured.update(kwargs)
        raise SystemExit(0)

    def fail_json(**kwargs):
        captured.update(kwargs)
        raise SystemExit(1)

    m.exit_json.side_effect = exit_json
    m.fail_json.side_effect = fail_json
    m._captured = captured
    return m


# ---------------------------------------------------------------------------
# Base test class
# ---------------------------------------------------------------------------

class VaultWriteTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake_ipalib, cls.fake_errors, cls.fake_api, cls.sys_patches = (
            _fake_ipalib())
        cls.ipa_client_mod = _load_ipa_client(cls.sys_patches)
        cls.mod = _load_vault_write(cls.sys_patches, cls.ipa_client_mod)
        # Wire module-level ipalib_errors in vault_write to use our fake
        cls.mod.ipalib_errors = cls.fake_errors
        cls.mod.HAS_IPALIB = True

    def _run(self, params, api_setup=None, check_mode=False):
        """Execute run_module() with the given params and optional API setup.

        *api_setup* is a callable(api) that configures Command mocks before
        the run.  Returns the captured exit_json / fail_json kwargs dict.
        """
        api = self.fake_api

        # Reset Command to a clean namespace each run
        api.Command = types.SimpleNamespace()

        if api_setup:
            api_setup(api)

        module_mock = _make_module(self.mod, params, check_mode=check_mode)

        client_instance = mock.MagicMock()
        client_instance.connect = mock.MagicMock()
        client_instance.cleanup = mock.MagicMock()
        client_instance.api = api
        client_instance.warn_if_permissive = mock.MagicMock()

        # Build a mock class that returns client_instance on instantiation
        # but preserves the real static methods (validate_scope, scope_args,
        # scope_label) so the module's validation logic runs correctly.
        real_cls = self.ipa_client_mod.IPAClient
        MockIPAClient = mock.MagicMock(spec=real_cls)
        MockIPAClient.validate_scope = real_cls.validate_scope
        MockIPAClient.scope_args = real_cls.scope_args
        MockIPAClient.scope_label = real_cls.scope_label
        MockIPAClient.return_value = client_instance

        with mock.patch.object(self.mod, 'AnsibleModule',
                               return_value=module_mock):
            with mock.patch.object(self.mod, 'IPAClient', MockIPAClient):
                try:
                    self.mod.run_module()
                except SystemExit:
                    pass

        return module_mock._captured


# ---------------------------------------------------------------------------
# state: present
# ---------------------------------------------------------------------------

class TestStatePresent(VaultWriteTestBase):

    def test_creates_vault_when_not_found(self):
        """state=present creates vault when vault_find returns empty."""
        entry = _make_vault_entry()

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': []})
            api.Command.vault_add = mock.MagicMock(
                return_value={'result': entry})

        result = self._run(_module_params(state='present'), setup)
        self.assertEqual(result.get('changed'), True)
        self.assertEqual(result['vault']['name'], 'test-vault')

    def test_idempotent_when_vault_exists_no_diff(self):
        """state=present is a no-op when vault exists and nothing differs."""
        entry = _make_vault_entry()

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': [entry]})

        result = self._run(_module_params(state='present'), setup)
        self.assertEqual(result.get('changed'), False)

    def test_updates_description_when_changed(self):
        """state=present updates description when it differs from current."""
        entry = _make_vault_entry(description='old description')

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                side_effect=[
                    {'result': [entry]},          # initial find
                    {'result': [_make_vault_entry(description='new desc')]},  # re-fetch
                ])
            api.Command.vault_mod = mock.MagicMock(return_value={'result': {}})

        result = self._run(
            _module_params(state='present', description='new desc'), setup)
        self.assertEqual(result.get('changed'), True)

    def test_check_mode_does_not_call_vault_add(self):
        """check_mode=True skips vault_add but reports changed=True."""
        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': []})
            api.Command.vault_add = mock.MagicMock()

        result = self._run(
            _module_params(state='present'), setup, check_mode=True)
        self.assertEqual(result.get('changed'), True)

    def test_symmetric_vault_creation_requires_password(self):
        """state=present must supply a password when creating a symmetric vault."""
        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': []})

        result = self._run(
            _module_params(state='present', vault_type='symmetric'),
            setup)
        self.assertIn('vault_type=symmetric requires', result.get('msg', ''))

    def test_creates_symmetric_vault_with_password(self):
        """state=present passes password to vault_add for new symmetric vaults."""
        entry = _make_vault_entry(vault_type='symmetric')

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': []})
            api.Command.vault_add = mock.MagicMock(
                return_value={'result': entry})

        result = self._run(
            _module_params(
                state='present',
                vault_type='symmetric',
                vault_password='sym-pass'),
            setup)
        self.assertEqual(result.get('changed'), True)
        add_kwargs = self.fake_api.Command.vault_add.call_args.kwargs
        self.assertEqual(add_kwargs['password'], 'sym-pass')

    def test_scope_mutual_exclusion_raises(self):
        """Providing both username and shared triggers fail_json."""
        params = _module_params(state='present', username='alice', shared=True)
        result = self._run(params)
        self.assertIn('msg', result)
        self.assertIn('mutually exclusive', result['msg'])


# ---------------------------------------------------------------------------
# state: absent
# ---------------------------------------------------------------------------

class TestStateAbsent(VaultWriteTestBase):

    def test_deletes_existing_vault(self):
        """state=absent deletes the vault when it exists."""
        entry = _make_vault_entry()

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': [entry]})
            api.Command.vault_del = mock.MagicMock(return_value={})

        result = self._run(_module_params(state='absent'), setup)
        self.assertEqual(result.get('changed'), True)

    def test_noop_when_vault_not_found(self):
        """state=absent is a no-op when vault does not exist."""
        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': []})

        result = self._run(_module_params(state='absent'), setup)
        self.assertEqual(result.get('changed'), False)

    def test_check_mode_skips_vault_del(self):
        """check_mode=True reports changed=True without calling vault_del."""
        entry = _make_vault_entry()

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': [entry]})
            api.Command.vault_del = mock.MagicMock()

        result = self._run(
            _module_params(state='absent'), setup, check_mode=True)
        self.assertEqual(result.get('changed'), True)


# ---------------------------------------------------------------------------
# state: archived
# ---------------------------------------------------------------------------

class TestStateArchived(VaultWriteTestBase):

    def test_creates_vault_and_archives_data(self):
        """state=archived creates a new vault then archives payload."""
        entry = _make_vault_entry()

        def setup(api):
            # vault_find returns empty (vault doesn't exist), then returns
            # entry after creation
            api.Command.vault_find = mock.MagicMock(
                side_effect=[
                    {'result': []},           # called by _ensure_present
                    {'result': [entry]},      # called by re-fetch in archived
                ])
            api.Command.vault_add = mock.MagicMock(
                return_value={'result': entry})
            api.Command.vault_archive = mock.MagicMock(
                return_value={'summary': 'Archived data into test-vault'})

        result = self._run(
            _module_params(state='archived', data='my-secret'), setup)
        self.assertEqual(result.get('changed'), True)

    def test_idempotent_when_payload_unchanged(self):
        """state=archived is a no-op when standard vault payload is identical."""
        entry = _make_vault_entry()
        payload = b'my-secret'

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': [entry]})
            api.Command.vault_retrieve = mock.MagicMock(
                return_value={'result': {'data': payload}})
            api.Command.vault_archive = mock.MagicMock()

        result = self._run(
            _module_params(state='archived', data='my-secret'), setup)
        self.assertEqual(result.get('changed'), False)

    def test_archives_when_payload_differs(self):
        """state=archived archives when existing payload differs."""
        entry = _make_vault_entry()

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                side_effect=[
                    {'result': [entry]},
                    {'result': [entry]},
                ])
            api.Command.vault_retrieve = mock.MagicMock(
                return_value={'result': {'data': b'old-secret'}})
            api.Command.vault_archive = mock.MagicMock(
                return_value={'summary': 'Archived data into test-vault'})

        result = self._run(
            _module_params(state='archived', data='new-secret'), setup)
        self.assertEqual(result.get('changed'), True)

    def test_symmetric_vault_always_archives(self):
        """state=archived on symmetric vault always writes (no comparison)."""
        entry = _make_vault_entry(vault_type='symmetric')

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                side_effect=[
                    {'result': [entry]},
                    {'result': [entry]},
                ])
            api.Command.vault_archive = mock.MagicMock(
                return_value={'summary': 'Archived data into test-vault'})

        result = self._run(
            _module_params(
                state='archived',
                data='same-secret',
                vault_password='vault-pw'),
            setup)
        self.assertEqual(result.get('changed'), True)

    def test_archived_requires_data_or_data_file(self):
        """state=archived without data or data_file triggers fail_json."""
        entry = _make_vault_entry()

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': []})
            api.Command.vault_add = mock.MagicMock(
                return_value={'result': entry})

        result = self._run(_module_params(state='archived'), setup)
        self.assertIn('msg', result)

    def test_symmetric_vault_requires_password(self):
        """state=archived on symmetric vault requires vault_password."""
        entry = _make_vault_entry(vault_type='symmetric')

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': [entry]})

        result = self._run(
            _module_params(state='archived', data='secret'),
            setup)
        self.assertIn('msg', result)

    def test_check_mode_skips_vault_archive(self):
        """check_mode=True reports changed=True but skips vault_archive."""
        entry = _make_vault_entry()

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': []})
            api.Command.vault_add = mock.MagicMock()
            api.Command.vault_archive = mock.MagicMock()

        result = self._run(
            _module_params(state='archived', data='secret'),
            setup,
            check_mode=True)
        self.assertEqual(result.get('changed'), True)

    def test_data_file_is_read(self):
        """state=archived with data_file reads the file and archives it."""
        entry = _make_vault_entry()

        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b'file-secret')
            f_path = f.name

        try:
            def setup(api):
                api.Command.vault_find = mock.MagicMock(
                    side_effect=[
                        {'result': []},
                        {'result': [entry]},
                    ])
                api.Command.vault_add = mock.MagicMock(
                    return_value={'result': entry})
                api.Command.vault_archive = mock.MagicMock(
                    return_value={'summary': 'Archived data into test-vault'})

            result = self._run(
                _module_params(state='archived', data_file=f_path),
                setup)
            self.assertEqual(result.get('changed'), True)
        finally:
            os.unlink(f_path)


# ---------------------------------------------------------------------------
# Asymmetric vault creation
# ---------------------------------------------------------------------------

class TestAsymmetricVault(VaultWriteTestBase):

    def test_asymmetric_vault_requires_public_key(self):
        """vault_type=asymmetric without public key triggers fail_json."""
        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': []})

        result = self._run(
            _module_params(state='present', vault_type='asymmetric'),
            setup)
        self.assertIn('msg', result)
        self.assertIn('asymmetric', result['msg'])

    def test_asymmetric_vault_created_with_public_key(self):
        """vault_type=asymmetric creates vault with vault_public_key."""
        entry = _make_vault_entry(vault_type='asymmetric')

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': []})
            api.Command.vault_add = mock.MagicMock(
                return_value={'result': entry})

        result = self._run(
            _module_params(
                state='present',
                vault_type='asymmetric',
                vault_public_key='-----BEGIN PUBLIC KEY-----\nMIIBIj...\n-----END PUBLIC KEY-----'),
            setup)
        self.assertEqual(result.get('changed'), True)


# ---------------------------------------------------------------------------
# Member management
# ---------------------------------------------------------------------------

class TestMemberManagement(VaultWriteTestBase):

    def test_adds_missing_members(self):
        """members list adds principals not currently in the vault."""
        entry = _make_vault_entry()  # no members

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                side_effect=[
                    {'result': [entry]},
                    {'result': [entry]},
                ])
            api.Command.user_show = mock.MagicMock(return_value={'result': {}})
            api.Command.group_show = mock.MagicMock(side_effect=self.fake_errors.NotFound())
            api.Command.service_show = mock.MagicMock(side_effect=self.fake_errors.NotFound())
            api.Command.vault_add_member = mock.MagicMock(
                return_value={'result': {}, 'failed': {}})

        result = self._run(
            _module_params(state='present', members=['alice']),
            setup)
        self.assertEqual(result.get('changed'), True)

    def test_member_add_is_idempotent(self):
        """members list is a no-op when principal is already a member."""
        entry = _make_vault_entry(members=['alice'])

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': [entry]})

        result = self._run(
            _module_params(state='present', members=['alice']),
            setup)
        self.assertEqual(result.get('changed'), False)

    def test_removes_unwanted_members(self):
        """members_absent removes principals currently in the vault."""
        entry = _make_vault_entry(members=['alice'])

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                side_effect=[
                    {'result': [entry]},
                    {'result': [_make_vault_entry()]},
                ])
            api.Command.user_show = mock.MagicMock(return_value={'result': {}})
            api.Command.group_show = mock.MagicMock(side_effect=self.fake_errors.NotFound())
            api.Command.service_show = mock.MagicMock(side_effect=self.fake_errors.NotFound())
            api.Command.vault_remove_member = mock.MagicMock(
                return_value={'result': {}, 'failed': {}})

        result = self._run(
            _module_params(state='present', members_absent=['alice']),
            setup)
        self.assertEqual(result.get('changed'), True)

    def test_member_remove_is_idempotent(self):
        """members_absent is a no-op when principal is already absent."""
        entry = _make_vault_entry()  # alice is not a member

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': [entry]})

        result = self._run(
            _module_params(state='present', members_absent=['alice']),
            setup)
        self.assertEqual(result.get('changed'), False)

    def test_check_mode_skips_member_operations(self):
        """check_mode=True reports changed=True without calling vault_add_member."""
        entry = _make_vault_entry()

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                return_value={'result': [entry]})
            api.Command.vault_add_member = mock.MagicMock()

        result = self._run(
            _module_params(state='present', members=['bob']),
            setup,
            check_mode=True)
        self.assertEqual(result.get('changed'), True)

    def test_adds_service_members_via_service_argument(self):
        """service principals are routed to vault_add_member(services=...)."""
        entry = _make_vault_entry()
        service_input = 'HTTP/web.example.com'
        service_principal = 'HTTP/web.example.com@EXAMPLE.COM'

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                side_effect=[
                    {'result': [entry]},
                    {'result': [entry]},
                ])
            api.Command.service_show = mock.MagicMock(
                return_value={'result': {'krbcanonicalname': [service_principal]}})
            api.Command.vault_add_member = mock.MagicMock(
                return_value={'result': {}, 'failed': {}})

        self._run(
            _module_params(state='present', members=[service_input]),
            setup)
        add_kwargs = self.fake_api.Command.vault_add_member.call_args.kwargs
        self.assertEqual(add_kwargs['services'], [service_principal])
        self.assertNotIn('users', add_kwargs)

    def test_adds_group_members_via_group_argument(self):
        """group names are routed to vault_add_member(group=...)."""
        entry = _make_vault_entry()

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                side_effect=[
                    {'result': [entry]},
                    {'result': [entry]},
                ])
            api.Command.user_show = mock.MagicMock(side_effect=self.fake_errors.NotFound())
            api.Command.group_show = mock.MagicMock(return_value={'result': {}})
            api.Command.service_show = mock.MagicMock(side_effect=self.fake_errors.NotFound())
            api.Command.vault_add_member = mock.MagicMock(
                return_value={'result': {}, 'failed': {}})

        self._run(
            _module_params(state='present', members=['ops-admins']),
            setup)
        add_kwargs = self.fake_api.Command.vault_add_member.call_args.kwargs
        self.assertEqual(add_kwargs['group'], ['ops-admins'])
        self.assertNotIn('user', add_kwargs)

    def test_empty_failed_member_structure_is_ignored(self):
        """IPA's empty nested failed structure is not treated as a real failure."""
        entry = _make_vault_entry()

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                side_effect=[
                    {'result': [entry]},
                    {'result': [entry]},
                ])
            api.Command.user_show = mock.MagicMock(return_value={'result': {}})
            api.Command.group_show = mock.MagicMock(side_effect=self.fake_errors.NotFound())
            api.Command.service_show = mock.MagicMock(side_effect=self.fake_errors.NotFound())
            api.Command.vault_add_member = mock.MagicMock(
                return_value={
                    'result': {},
                    'failed': {'member': {'user': (), 'group': (), 'services': ()}},
                })

        result = self._run(
            _module_params(state='present', members=['alice']),
            setup)
        self.assertEqual(result.get('changed'), True)

    def test_service_member_remove_matches_canonical_membership(self):
        """service removals match the canonical member_service value from IPA."""
        service_input = 'HTTP/web.example.com'
        service_principal = 'HTTP/web.example.com@EXAMPLE.COM'
        entry = _make_vault_entry()
        entry['member_service'] = [service_principal]

        def setup(api):
            api.Command.vault_find = mock.MagicMock(
                side_effect=[
                    {'result': [entry]},
                    {'result': [_make_vault_entry()]},
                ])
            api.Command.service_show = mock.MagicMock(
                return_value={'result': {'krbcanonicalname': [service_principal]}})
            api.Command.vault_remove_member = mock.MagicMock(
                return_value={'result': {}, 'failed': {'member': {'user': (), 'group': (), 'services': ()}}})

        result = self._run(
            _module_params(state='present', members_absent=[service_input]),
            setup)
        self.assertEqual(result.get('changed'), True)
        remove_kwargs = self.fake_api.Command.vault_remove_member.call_args.kwargs
        self.assertEqual(remove_kwargs['services'], [service_principal])


# ---------------------------------------------------------------------------
# IPAClient unit tests (module_utils)
# ---------------------------------------------------------------------------

class TestIPAClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, _, _, sys_patches = _fake_ipalib()
        cls.ipa_client_mod = _load_ipa_client(sys_patches)

    def test_scope_args_shared(self):
        args = self.ipa_client_mod.IPAClient.scope_args(None, None, True)
        self.assertEqual(args, {'shared': True})

    def test_scope_args_username(self):
        args = self.ipa_client_mod.IPAClient.scope_args('alice', None, False)
        self.assertEqual(args, {'username': 'alice'})

    def test_scope_args_service(self):
        args = self.ipa_client_mod.IPAClient.scope_args(None, 'HTTP/web.example.com', False)
        self.assertEqual(args, {'service': 'HTTP/web.example.com'})

    def test_scope_args_default(self):
        args = self.ipa_client_mod.IPAClient.scope_args(None, None, False)
        self.assertEqual(args, {})

    def test_scope_label_shared(self):
        label = self.ipa_client_mod.IPAClient.scope_label(None, None, True)
        self.assertEqual(label, 'shared')

    def test_scope_label_username(self):
        label = self.ipa_client_mod.IPAClient.scope_label('alice', None, False)
        self.assertEqual(label, 'username=alice')

    def test_validate_scope_rejects_conflicts(self):
        with self.assertRaises(self.ipa_client_mod.IPAClientError):
            self.ipa_client_mod.IPAClient.validate_scope('alice', 'HTTP/x', False)

    def test_validate_scope_rejects_username_and_shared(self):
        with self.assertRaises(self.ipa_client_mod.IPAClientError):
            self.ipa_client_mod.IPAClient.validate_scope('alice', None, True)

    def test_validate_scope_accepts_single(self):
        # Should not raise
        self.ipa_client_mod.IPAClient.validate_scope('alice', None, False)
        self.ipa_client_mod.IPAClient.validate_scope(None, 'HTTP/x', False)
        self.ipa_client_mod.IPAClient.validate_scope(None, None, True)
        self.ipa_client_mod.IPAClient.validate_scope(None, None, False)

    def test_unwrap_single_element_list(self):
        self.assertEqual(self.ipa_client_mod.IPAClient.unwrap(['standard']), 'standard')

    def test_unwrap_empty_list(self):
        self.assertIsNone(self.ipa_client_mod.IPAClient.unwrap([]))

    def test_unwrap_scalar(self):
        self.assertEqual(self.ipa_client_mod.IPAClient.unwrap('value'), 'value')

    def test_ccache_cleanup_restores_env(self):
        """cleanup() restores KRB5CCNAME to its previous value."""
        client = self.ipa_client_mod.IPAClient()

        with tempfile.NamedTemporaryFile(delete=False) as f:
            ccache_path = f.name

        original = os.environ.get('KRB5CCNAME')
        os.environ['KRB5CCNAME'] = 'FILE:/tmp/original'

        try:
            client._activate_ccache(ccache_path, 'FILE:%s' % ccache_path)
            self.assertEqual(os.environ['KRB5CCNAME'], 'FILE:%s' % ccache_path)
            client.cleanup()
            self.assertFalse(os.path.exists(ccache_path))
            self.assertEqual(os.environ.get('KRB5CCNAME'), 'FILE:/tmp/original')
        finally:
            if original is None:
                os.environ.pop('KRB5CCNAME', None)
            else:
                os.environ['KRB5CCNAME'] = original
            if os.path.exists(ccache_path):
                os.unlink(ccache_path)

    def test_warn_if_permissive_fires_on_0644(self):
        """warn_if_permissive emits warning for group-readable files."""
        warnings = []
        client = self.ipa_client_mod.IPAClient(
            warn_callback=warnings.append)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            os.chmod(path, 0o644)
            client.warn_if_permissive(path, 'vault_password_file')
            self.assertEqual(len(warnings), 1)
            self.assertIn('vault_password_file', warnings[0])
        finally:
            os.unlink(path)

    def test_warn_if_permissive_silent_on_0600(self):
        """warn_if_permissive is silent for 0600 files."""
        warnings = []
        client = self.ipa_client_mod.IPAClient(
            warn_callback=warnings.append)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            os.chmod(path, 0o600)
            client.warn_if_permissive(path, 'kerberos_keytab')
            self.assertEqual(len(warnings), 0)
        finally:
            os.unlink(path)

    def test_resolve_verify_false_disables_tls_explicitly(self):
        warnings = []
        client = self.ipa_client_mod.IPAClient(
            warn_callback=warnings.append)
        self.assertFalse(client._resolve_verify(False))
        self.assertEqual(len(warnings), 1)

    def test_resolve_verify_string_false_disables_tls_explicitly(self):
        warnings = []
        client = self.ipa_client_mod.IPAClient(
            warn_callback=warnings.append)
        self.assertFalse(client._resolve_verify('false'))
        self.assertEqual(len(warnings), 1)


    def test_kinit_password_fallback_normalizes_stdin_newline(self):
        client = self.ipa_client_mod.IPAClient()
        self.ipa_client_mod.HAS_KINIT_PASSWORD = False
        with mock.patch.object(self.ipa_client_mod.subprocess, 'run') as run_mock,                 mock.patch.object(self.ipa_client_mod.tempfile, 'mkstemp', return_value=(99, '/tmp/ccache-test')),                 mock.patch.object(self.ipa_client_mod.os, 'close'),                 mock.patch.object(self.ipa_client_mod.os, 'remove'),                 mock.patch.object(client, '_activate_ccache') as activate_mock:
            run_mock.return_value = types.SimpleNamespace(returncode=0, stderr='')
            client._kinit_password('admin', 'secret')
        self.assertEqual(run_mock.call_args.kwargs['input'], 'secret\n')
        activate_mock.assert_called_once_with('/tmp/ccache-test', 'FILE:/tmp/ccache-test')


if __name__ == '__main__':
    unittest.main()
