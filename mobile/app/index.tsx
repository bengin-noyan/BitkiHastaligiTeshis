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
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { login } from '../src/services/api';
import { COLORS, FONTS, SHADOW_TINT } from '../src/constants/theme';

export default function LoginScreen() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    // Validate inputs
    if (!username.trim()) {
      setError('Lütfen kullanıcı adınızı girin.');
      return;
    }
    if (!password.trim()) {
      setError('Lütfen şifrenizi girin.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const result = await login(username.trim(), password);
      if (result.success) {
        router.replace({
          pathname: '/home',
          params: { username: result.username || username.trim() },
        });
      } else {
        setError('Giriş başarısız. Kullanıcı adı veya şifre hatalı.');
      }
    } catch (err: any) {
      setError(err.message || 'Bir hata oluştu. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Top badge pill (app.py .lp-badge) */}
          <View style={styles.badgePill}>
            <View style={styles.badgeDot} />
            <Text style={styles.badgePillText}>Yapay Zekâ Destekli Teşhis</Text>
          </View>

          {/* App Icon (app.py .lp-icon — zümrüt yumuşak kutu) */}
          <View style={styles.iconContainer}>
            <View style={styles.iconBox}>
              <Text style={styles.iconEmoji}>🌿</Text>
            </View>
          </View>

          {/* Title */}
          <Text style={styles.title}>Tarımsal Analiz{'\n'}Sistemi</Text>
          <Text style={styles.subtitle}>
            Yapay zekâ destekli bitki hastalığı{'\n'}teşhis platformu
          </Text>

          {/* Login Card */}
          <View style={styles.card}>
            {/* Error Message */}
            {error !== '' && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorIcon}>⚠️</Text>
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            {/* Username Input */}
            <View style={styles.inputWrapper}>
              <Text style={styles.inputLabel}>Kullanıcı Adı</Text>
              <View style={styles.inputContainer}>
                <Text style={styles.inputIcon}>👤</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Kullanıcı adınızı girin"
                  placeholderTextColor={COLORS.textMuted}
                  value={username}
                  onChangeText={(text) => {
                    setUsername(text);
                    if (error) setError('');
                  }}
                  autoCapitalize="none"
                  autoCorrect={false}
                  editable={!loading}
                />
              </View>
            </View>

            {/* Password Input */}
            <View style={styles.inputWrapper}>
              <Text style={styles.inputLabel}>Şifre</Text>
              <View style={styles.inputContainer}>
                <Text style={styles.inputIcon}>🔒</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Şifrenizi girin"
                  placeholderTextColor={COLORS.textMuted}
                  value={password}
                  onChangeText={(text) => {
                    setPassword(text);
                    if (error) setError('');
                  }}
                  secureTextEntry
                  editable={!loading}
                  onSubmitEditing={handleLogin}
                  returnKeyType="go"
                />
              </View>
            </View>

            {/* Login Button */}
            <TouchableOpacity
              style={[
                styles.loginButton,
                loading && styles.loginButtonDisabled,
              ]}
              onPress={handleLogin}
              disabled={loading}
              activeOpacity={0.8}
            >
              {loading ? (
                <View style={styles.loadingRow}>
                  <ActivityIndicator size="small" color={COLORS.white} />
                  <Text style={styles.loginButtonText}>
                    {'  '}Giriş yapılıyor...
                  </Text>
                </View>
              ) : (
                <Text style={styles.loginButtonText}>Giriş Yap</Text>
              )}
            </TouchableOpacity>
          </View>

          {/* Bottom Badge */}
          <View style={styles.bottomBadge}>
            <Text style={styles.badgeText}>
              © 2026 Tarımsal Analiz Sistemi
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// ─── Styles ──────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.primarySoft,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 28,
    paddingVertical: 40,
  },
  // Badge pill (app.py .lp-badge)
  badgePill: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'center',
    gap: 7,
    backgroundColor: COLORS.white,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 100,
    paddingHorizontal: 14,
    paddingVertical: 7,
    marginBottom: 24,
  },
  badgeDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: COLORS.primary,
  },
  badgePillText: {
    fontFamily: FONTS.semibold,
    fontSize: 12,
    color: COLORS.textSoft,
    letterSpacing: 0.2,
  },
  iconContainer: {
    alignItems: 'center',
    marginBottom: 22,
  },
  iconBox: {
    width: 76,
    height: 76,
    borderRadius: 20,
    backgroundColor: COLORS.successSoft,
    borderWidth: 1,
    borderColor: COLORS.successBorder,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.14,
    shadowRadius: 16,
    elevation: 6,
  },
  iconEmoji: {
    fontSize: 34,
  },
  title: {
    fontFamily: FONTS.extrabold,
    fontSize: 30,
    color: COLORS.textDark,
    textAlign: 'center',
    lineHeight: 38,
    letterSpacing: -0.8,
    marginBottom: 10,
  },
  subtitle: {
    fontFamily: FONTS.regular,
    fontSize: 15,
    color: COLORS.textSoft,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 34,
  },
  card: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 16,
    padding: 24,
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 18,
    elevation: 4,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.redSoft,
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: COLORS.redBorder,
  },
  errorIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  errorText: {
    flex: 1,
    fontFamily: FONTS.medium,
    fontSize: 13,
    color: COLORS.red,
    lineHeight: 18,
  },
  inputWrapper: {
    marginBottom: 18,
  },
  inputLabel: {
    fontFamily: FONTS.semibold,
    fontSize: 13,
    color: COLORS.textMid,
    marginBottom: 8,
    marginLeft: 4,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.inputBg,
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: COLORS.border,
    paddingHorizontal: 14,
    height: 52,
  },
  inputIcon: {
    fontSize: 18,
    marginRight: 10,
  },
  input: {
    flex: 1,
    fontFamily: FONTS.medium,
    fontSize: 15,
    color: COLORS.textDark,
    paddingVertical: 0,
  },
  loginButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 12,
    height: 52,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.28,
    shadowRadius: 12,
    elevation: 4,
  },
  loginButtonDisabled: {
    opacity: 0.7,
  },
  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  loginButtonText: {
    fontFamily: FONTS.bold,
    fontSize: 16,
    color: COLORS.white,
    letterSpacing: 0.2,
  },
  bottomBadge: {
    alignItems: 'center',
    marginTop: 34,
    paddingVertical: 12,
  },
  badgeText: {
    fontFamily: FONTS.medium,
    fontSize: 12,
    color: COLORS.textMuted,
    textAlign: 'center',
    letterSpacing: 0.3,
  },
});
