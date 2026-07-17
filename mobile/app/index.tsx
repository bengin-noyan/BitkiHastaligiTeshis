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
          {/* Top Decorative Dots */}
          <View style={styles.dotsRow}>
            <View style={[styles.dot, { backgroundColor: '#7DA78C' }]} />
            <View style={[styles.dot, { backgroundColor: '#A3C4AF' }]} />
            <View style={[styles.dot, { backgroundColor: '#D4E6DA' }]} />
          </View>

          {/* App Icon */}
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
                  placeholderTextColor="#94a3b8"
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
                  placeholderTextColor="#94a3b8"
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
                  <ActivityIndicator size="small" color="#ffffff" />
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
            <Text style={styles.badgeLine}>🎓</Text>
            <Text style={styles.badgeText}>
              Pamukkale Üniversitesi · YBS Bitirme Projesi
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
    backgroundColor: '#f0f5f2',
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
  dotsRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
    marginBottom: 28,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  iconContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  iconBox: {
    width: 80,
    height: 80,
    borderRadius: 24,
    backgroundColor: '#7DA78C',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#7DA78C',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  iconEmoji: {
    fontSize: 36,
  },
  title: {
    fontSize: 30,
    fontWeight: '800',
    color: '#0f172a',
    textAlign: 'center',
    lineHeight: 38,
    letterSpacing: -0.5,
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 15,
    color: '#64748b',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 36,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 24,
    shadowColor: '#0f172a',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: 16,
    elevation: 4,
    borderWidth: 1,
    borderColor: '#e8ede9',
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fef2f2',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#fecaca',
  },
  errorIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  errorText: {
    flex: 1,
    fontSize: 13,
    color: '#dc2626',
    lineHeight: 18,
  },
  inputWrapper: {
    marginBottom: 18,
  },
  inputLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#334155',
    marginBottom: 8,
    marginLeft: 4,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8faf8',
    borderRadius: 14,
    borderWidth: 1.5,
    borderColor: '#e2e8f0',
    paddingHorizontal: 14,
    height: 52,
  },
  inputIcon: {
    fontSize: 18,
    marginRight: 10,
  },
  input: {
    flex: 1,
    fontSize: 15,
    color: '#0f172a',
    paddingVertical: 0,
  },
  loginButton: {
    backgroundColor: '#7DA78C',
    borderRadius: 14,
    height: 52,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
    shadowColor: '#7DA78C',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
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
    fontSize: 16,
    fontWeight: '700',
    color: '#ffffff',
    letterSpacing: 0.3,
  },
  bottomBadge: {
    alignItems: 'center',
    marginTop: 36,
    paddingVertical: 12,
  },
  badgeLine: {
    fontSize: 20,
    marginBottom: 6,
  },
  badgeText: {
    fontSize: 12,
    color: '#94a3b8',
    textAlign: 'center',
    letterSpacing: 0.2,
  },
});
