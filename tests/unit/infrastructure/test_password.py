from auth_api.internal.infrastructure.password import WerkzeugHashProvider


class TestWerkzeugHashProvider:
    """РўРµСЃС‚С‹ С…РµС€-РїСЂРѕРІР°Р№РґРµСЂР° РЅР° РѕСЃРЅРѕРІРµ Werkzeug."""

    def setup_method(self):
        self.hasher = WerkzeugHashProvider()

    def test_hash_data_returns_non_empty_string(self):
        """hash_data РІРѕР·РІСЂР°С‰Р°РµС‚ РЅРµРїСѓСЃС‚СѓСЋ СЃС‚СЂРѕРєСѓ."""
        result = self.hasher.hash_data("my_password")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_differs_from_original(self):
        """РҐСЌС€ РЅРµ СЃРѕРІРїР°РґР°РµС‚ СЃ РёСЃС…РѕРґРЅРѕР№ СЃС‚СЂРѕРєРѕР№."""
        password = "secret123"
        hashed = self.hasher.hash_data(password)
        assert hashed != password

    def test_verify_correct_password(self):
        """verify_data РІРѕР·РІСЂР°С‰Р°РµС‚ True РґР»СЏ РІРµСЂРЅРѕРіРѕ РїР°СЂРѕР»СЏ."""
        password = "correct_password"
        hashed = self.hasher.hash_data(password)
        assert self.hasher.verify_data(hashed, password) is True

    def test_verify_wrong_password(self):
        """verify_data РІРѕР·РІСЂР°С‰Р°РµС‚ False РґР»СЏ РЅРµРІРµСЂРЅРѕРіРѕ РїР°СЂРѕР»СЏ."""
        hashed = self.hasher.hash_data("correct_password")
        assert self.hasher.verify_data(hashed, "wrong_password") is False

    def test_different_hashes_for_same_password(self):
        """Р”РІР° С…СЌС€Р° РѕРґРЅРѕРіРѕ РїР°СЂРѕР»СЏ СЂР°Р·Р»РёС‡Р°СЋС‚СЃСЏ (salt)."""
        password = "same_password"
        hash1 = self.hasher.hash_data(password)
        hash2 = self.hasher.hash_data(password)
        assert hash1 != hash2

    def test_both_hashes_verify(self):
        """РћР±Р° С…СЌС€Р° РѕРґРЅРѕРіРѕ РїР°СЂРѕР»СЏ РїСЂРѕС…РѕРґСЏС‚ РІРµСЂРёС„РёРєР°С†РёСЋ."""
        password = "same_password"
        hash1 = self.hasher.hash_data(password)
        hash2 = self.hasher.hash_data(password)
        assert self.hasher.verify_data(hash1, password) is True
        assert self.hasher.verify_data(hash2, password) is True

