import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ImageBackground,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { login, register } from '../src/services/api';
import { COLORS, FONTS, SHADOW_TINT } from '../src/constants/theme';
import { LANG_OPTIONS, format, apiErrorText } from '../src/constants/i18n';
import { useLanguage } from '../src/context/LanguageContext';

// görseller app.py'deki assets klasöründen kopyalandı, ikisi de aynı
const BG_IMAGE = require('../assets/login_bg.jpg');
const LOGO = require('../assets/logo_transparent.png');

type TabKey = 'login' | 'register';

export default function LoginScreen() {
  const router = useRouter();
  const { lang, setLang, T } = useLanguage();
  const isTR = lang === 'tr';
  const [tab, setTab] = useState<TabKey>('login');

  // giriş sekmesi
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // kayıt sekmesi
  const [newUser, setNewUser] = useState('');
  const [newPass, setNewPass] = useState('');
  const [newPass2, setNewPass2] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const switchTab = (next: TabKey) => {
    setTab(next);
    setError('');
    setSuccess('');
  };

  // ----- giriş yap -----
  const handleLogin = async () => {
    if (!username.trim()) {
      setError(T.err_enter_user);
      return;
    }
    if (!password.trim()) {
      setError(T.err_enter_pass);
      return;
    }

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await login(username.trim().toLowerCase(), password.trim());
      if (result.success) {
        router.replace({
          pathname: '/home',
          params: { username: result.username || username.trim() },
        });
      } else {
        setError(T.err_invalid);
      }
    } catch (err: any) {
      setError(apiErrorText(err?.code, T, isTR ? err?.message : undefined));
    } finally {
      setLoading(false);
    }
  };

  // ----- kayıt ol -----
  const handleRegister = async () => {
    if (!newUser.trim() || !newPass.trim()) {
      setError(T.warn_fill_all);
      return;
    }
    if (newPass !== newPass2) {
      setError(T.err_mismatch);
      return;
    }

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await register(newUser.trim().toLowerCase(), newPass.trim());
      if (result.success) {
        setSuccess(format(T.success_reg, newUser.trim()));
        setNewUser('');
        setNewPass('');
        setNewPass2('');
      } else {
        // sunucu türkçe mesaj dönüyor, arayüz ingilizceyse kendi metnimizi basıyoruz
        setError(lang === 'tr' ? result.message || T.err_user_taken : T.err_user_taken);
      }
    } catch (err: any) {
      setError(apiErrorText(err?.code, T, isTR ? err?.message : T.err_register));
    } finally {
      setLoading(false);
    }
  };

  return (
    <ImageBackground source={BG_IMAGE} style={styles.bg} resizeMode="cover">
      {/* app.py'deki hafif beyaz katman, üstteki yazılar okunsun diye */}
      <View style={styles.overlay} />

      <SafeAreaView style={styles.container}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          style={styles.keyboardView}
        >
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            {/* dil seçici (web'deki ortalanmış hap kutusu) */}
            <View style={styles.langSwitch}>
              {LANG_OPTIONS.map((opt) => (
                <TouchableOpacity
                  key={opt.key}
                  style={[
                    styles.langOption,
                    lang === opt.key && styles.langOptionActive,
                  ]}
                  onPress={() => setLang(opt.key)}
                  activeOpacity={0.7}
                >
                  <Text
                    style={[
                      styles.langOptionText,
                      lang === opt.key && styles.langOptionTextActive,
                    ]}
                  >
                    {opt.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* logo, arka planın üstünde serbest duruyor */}
            <Image source={LOGO} style={styles.logo} resizeMode="contain" />

            {/* beyaz giriş kartı (app.py .st-key-login_panel) */}
            <View style={styles.card}>
              {/* Giriş Yap / Kayıt Ol sekmeleri */}
              <View style={styles.tabBar}>
                <TouchableOpacity
                  style={styles.tabItem}
                  onPress={() => switchTab('login')}
                  activeOpacity={0.7}
                >
                  <Text
                    style={[
                      styles.tabText,
                      tab === 'login' && styles.tabTextActive,
                    ]}
                  >
                    {T.tab_login}
                  </Text>
                  <View
                    style={[
                      styles.tabUnderline,
                      tab === 'login' && styles.tabUnderlineActive,
                    ]}
                  />
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.tabItem}
                  onPress={() => switchTab('register')}
                  activeOpacity={0.7}
                >
                  <Text
                    style={[
                      styles.tabText,
                      tab === 'register' && styles.tabTextActive,
                    ]}
                  >
                    {T.tab_register}
                  </Text>
                  <View
                    style={[
                      styles.tabUnderline,
                      tab === 'register' && styles.tabUnderlineActive,
                    ]}
                  />
                </TouchableOpacity>
              </View>

              {/* uyarı ve bilgi mesajları */}
              {error !== '' && (
                <View style={styles.errorContainer}>
                  <Text style={styles.errorText}>{error}</Text>
                </View>
              )}
              {success !== '' && (
                <View style={styles.successContainer}>
                  <Text style={styles.successText}>{success}</Text>
                </View>
              )}

              {tab === 'login' ? (
                <>
                  <View style={styles.inputWrapper}>
                    <Text style={styles.inputLabel}>{T.username}</Text>
                    <View style={styles.inputContainer}>
                      <TextInput
                        style={styles.input}
                        placeholder={T.username_ph}
                        placeholderTextColor={COLORS.textMuted}
                        value={username}
                        onChangeText={(t) => {
                          setUsername(t);
                          if (error) setError('');
                        }}
                        autoCapitalize="none"
                        autoCorrect={false}
                        editable={!loading}
                      />
                    </View>
                  </View>

                  <View style={styles.inputWrapper}>
                    <Text style={styles.inputLabel}>{T.password}</Text>
                    <View style={styles.inputContainer}>
                      <TextInput
                        style={styles.input}
                        placeholder={T.password_ph}
                        placeholderTextColor={COLORS.textMuted}
                        value={password}
                        onChangeText={(t) => {
                          setPassword(t);
                          if (error) setError('');
                        }}
                        secureTextEntry={!showPassword}
                        editable={!loading}
                        onSubmitEditing={handleLogin}
                        returnKeyType="go"
                      />
                      {/* şifre göster/gizle, webdeki göz butonunun aynısı */}
                      <TouchableOpacity
                        onPress={() => setShowPassword((prev) => !prev)}
                        activeOpacity={0.6}
                        style={styles.eyeButton}
                      >
                        <Text style={styles.eyeIcon}>
                          {showPassword ? '🙈' : '👁'}
                        </Text>
                      </TouchableOpacity>
                    </View>
                  </View>

                  <TouchableOpacity
                    style={[styles.primaryButton, loading && styles.buttonDisabled]}
                    onPress={handleLogin}
                    disabled={loading}
                    activeOpacity={0.85}
                  >
                    {loading ? (
                      <View style={styles.loadingRow}>
                        <ActivityIndicator size="small" color={COLORS.white} />
                        <Text style={styles.primaryButtonText}>
                          {'  '}
                          {T.loading_login}
                        </Text>
                      </View>
                    ) : (
                      <Text style={styles.primaryButtonText}>{T.btn_login}</Text>
                    )}
                  </TouchableOpacity>
                </>
              ) : (
                <>
                  <View style={styles.inputWrapper}>
                    <Text style={styles.inputLabel}>{T.new_username}</Text>
                    <View style={styles.inputContainer}>
                      <TextInput
                        style={styles.input}
                        placeholder={T.new_username_ph}
                        placeholderTextColor={COLORS.textMuted}
                        value={newUser}
                        onChangeText={(t) => {
                          setNewUser(t);
                          if (error) setError('');
                        }}
                        autoCapitalize="none"
                        autoCorrect={false}
                        editable={!loading}
                      />
                    </View>
                  </View>

                  <View style={styles.inputWrapper}>
                    <Text style={styles.inputLabel}>{T.new_password}</Text>
                    <View style={styles.inputContainer}>
                      <TextInput
                        style={styles.input}
                        placeholder={T.new_password_ph}
                        placeholderTextColor={COLORS.textMuted}
                        value={newPass}
                        onChangeText={(t) => {
                          setNewPass(t);
                          if (error) setError('');
                        }}
                        secureTextEntry
                        editable={!loading}
                      />
                    </View>
                  </View>

                  <View style={styles.inputWrapper}>
                    <Text style={styles.inputLabel}>{T.confirm_password}</Text>
                    <View style={styles.inputContainer}>
                      <TextInput
                        style={styles.input}
                        placeholder={T.confirm_password_ph}
                        placeholderTextColor={COLORS.textMuted}
                        value={newPass2}
                        onChangeText={(t) => {
                          setNewPass2(t);
                          if (error) setError('');
                        }}
                        secureTextEntry
                        editable={!loading}
                        onSubmitEditing={handleRegister}
                        returnKeyType="go"
                      />
                    </View>
                  </View>

                  <TouchableOpacity
                    style={[styles.primaryButton, loading && styles.buttonDisabled]}
                    onPress={handleRegister}
                    disabled={loading}
                    activeOpacity={0.85}
                  >
                    {loading ? (
                      <View style={styles.loadingRow}>
                        <ActivityIndicator size="small" color={COLORS.white} />
                        <Text style={styles.primaryButtonText}>
                          {'  '}
                          {T.loading_register}
                        </Text>
                      </View>
                    ) : (
                      <Text style={styles.primaryButtonText}>{T.btn_register}</Text>
                    )}
                  </TouchableOpacity>
                </>
              )}

              {/* alttaki istatistik hapları (app.py .lp-stats) */}
              <View style={styles.statsRow}>
                <View style={styles.pill}>
                  <Text style={styles.pillText}>
                    <Text style={styles.pillStrong}>
                      {lang === 'tr' ? '%94+' : '94%+'}
                    </Text>{' '}
                    {T.pill_accuracy}
                  </Text>
                </View>
                <View style={styles.pill}>
                  <Text style={styles.pillText}>
                    <Text style={styles.pillStrong}>
                      {lang === 'tr' ? '<1sn' : '<1s'}
                    </Text>{' '}
                    {T.pill_analysis}
                  </Text>
                </View>
                <View style={styles.pill}>
                  <Text style={styles.pillText}>
                    <Text style={styles.pillStrong}>29</Text> {T.pill_classes}
                  </Text>
                </View>
              </View>
            </View>

            {/* telif satırı (app.py .lp-footer-note) */}
            <View style={styles.footerNote}>
              <Text style={styles.footerNoteText}>{T.copyright}</Text>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </ImageBackground>
  );
}

// ----- stiller (app.py giriş ekranına göre yazıldı) -----

const styles = StyleSheet.create({
  bg: {
    flex: 1,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(248,250,252,0.10)',
  },
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 20,
    paddingVertical: 24,
  },

  // dil seçici, webdeki ortalanmış beyaz hap kutusu
  langSwitch: {
    flexDirection: 'row',
    alignSelf: 'center',
    alignItems: 'center',
    gap: 4,
    backgroundColor: COLORS.white,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 100,
    paddingHorizontal: 5,
    paddingVertical: 4,
    marginBottom: 10,
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 2,
  },
  langOption: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 100,
  },
  langOptionActive: {
    backgroundColor: COLORS.primarySoft,
  },
  langOptionText: {
    fontFamily: FONTS.medium,
    fontSize: 13,
    color: COLORS.textSoft,
  },
  langOptionTextActive: {
    fontFamily: FONTS.semibold,
    color: COLORS.primaryText,
  },

  // logo şeffaf png, kutusuz. webdeki drop-shadow'un rn karşılığı
  logo: {
    width: '86%',
    height: 118,
    alignSelf: 'center',
    marginBottom: 14,
  },

  // beyaz form kartı (.st-key-login_panel)
  card: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: COLORS.border,
    paddingHorizontal: 22,
    paddingTop: 14,
    paddingBottom: 18,
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 0.22,
    shadowRadius: 30,
    elevation: 10,
  },

  // sekmeler (st.tabs görünümü)
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 22,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
    marginBottom: 16,
  },
  tabItem: {
    alignItems: 'center',
    paddingTop: 6,
  },
  tabText: {
    fontFamily: FONTS.semibold,
    fontSize: 14,
    color: COLORS.textSoft,
    paddingBottom: 8,
  },
  tabTextActive: {
    color: COLORS.primary,
  },
  tabUnderline: {
    height: 2,
    width: '100%',
    backgroundColor: 'transparent',
    borderRadius: 2,
  },
  tabUnderlineActive: {
    backgroundColor: COLORS.primary,
  },

  errorContainer: {
    backgroundColor: COLORS.redSoft,
    borderRadius: 10,
    padding: 11,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: COLORS.redBorder,
  },
  errorText: {
    fontFamily: FONTS.medium,
    fontSize: 13,
    color: COLORS.red,
    lineHeight: 18,
  },
  successContainer: {
    backgroundColor: COLORS.primarySoft,
    borderRadius: 10,
    padding: 11,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: COLORS.primaryBorder,
  },
  successText: {
    fontFamily: FONTS.medium,
    fontSize: 13,
    color: COLORS.primaryText,
    lineHeight: 18,
  },

  inputWrapper: {
    marginBottom: 14,
  },
  inputLabel: {
    fontFamily: FONTS.semibold,
    fontSize: 13,
    color: '#1e293b',
    marginBottom: 6,
  },
  // açık gri zemin + kenarlık (webdeki #eef2f7 / #cbd5e1)
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.inputBg,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: COLORS.inputBorder,
    paddingHorizontal: 14,
    height: 48,
  },
  input: {
    flex: 1,
    fontFamily: FONTS.semibold,
    fontSize: 15,
    color: COLORS.textDark,
    paddingVertical: 0,
  },
  eyeButton: {
    paddingLeft: 8,
    paddingVertical: 6,
  },
  eyeIcon: {
    fontSize: 16,
  },

  primaryButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 10,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 4,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 4,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  primaryButtonText: {
    fontFamily: FONTS.bold,
    fontSize: 15,
    color: COLORS.white,
    letterSpacing: 0.2,
  },

  // istatistik hapları
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    flexWrap: 'wrap',
    gap: 7,
    marginTop: 16,
  },
  pill: {
    backgroundColor: '#f9fafb',
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 100,
    paddingHorizontal: 11,
    paddingVertical: 6,
  },
  pillText: {
    fontFamily: FONTS.medium,
    fontSize: 11,
    color: COLORS.textSoft,
  },
  pillStrong: {
    fontFamily: FONTS.bold,
    color: COLORS.textDark,
  },

  // telif satırı, arka planın üstünde okunsun diye beyaz hap
  footerNote: {
    alignSelf: 'center',
    marginTop: 16,
    backgroundColor: 'rgba(255,255,255,0.92)',
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 100,
    paddingHorizontal: 14,
    paddingVertical: 6,
  },
  footerNoteText: {
    fontFamily: FONTS.medium,
    fontSize: 11,
    color: '#475569',
  },
});
