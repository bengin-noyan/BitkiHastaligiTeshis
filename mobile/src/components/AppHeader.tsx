// ─────────────────────────────────────────────────────────────────────
// Uygulama başlığı — app.py'deki koyu yeşil admin-panel şeridinin
// karşılığı. Ana sayfa ve geçmiş sayfası aynı başlığı paylaşır.
// ─────────────────────────────────────────────────────────────────────

import React, { useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { COLORS, FONTS, SHADOW_TINT } from '../constants/theme';
import { useLanguage } from '../context/LanguageContext';

export default function AppHeader({ username }: { username: string }) {
  const router = useRouter();
  const { T } = useLanguage();

  const handleLogout = useCallback(() => {
    Alert.alert(T.logout_title, T.logout_msg, [
      { text: T.cancel, style: 'cancel' },
      {
        text: T.logout_confirm,
        style: 'destructive',
        onPress: () => router.replace('/'),
      },
    ]);
  }, [router, T]);

  return (
    <View style={styles.header}>
      <View style={styles.headerAccent} />
      <View style={styles.headerContent}>
        <View style={styles.headerLeft}>
          <Text style={styles.headerTitle}>PlantDetective</Text>
          <Text style={styles.headerSubtitle}>{T.header_sub}</Text>
        </View>
        <TouchableOpacity
          style={styles.logoutButton}
          onPress={handleLogout}
          activeOpacity={0.7}
        >
          <Text style={styles.logoutText}>{T.btn_logout}</Text>
        </TouchableOpacity>
      </View>
      <View style={styles.greetingRow}>
        <View style={styles.greetingDot} />
        <Text style={styles.greetingText}>
          {T.greeting}
          <Text style={styles.greetingName}>{username}</Text>
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    backgroundColor: COLORS.darkGreen,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.06)',
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.18,
    shadowRadius: 10,
    elevation: 6,
  },
  headerAccent: {
    height: 4,
    backgroundColor: '#34c46a',
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 4,
  },
  headerLeft: {
    flex: 1,
  },
  headerTitle: {
    fontFamily: FONTS.extrabold,
    fontSize: 22,
    color: COLORS.white,
    letterSpacing: -0.3,
  },
  headerSubtitle: {
    fontFamily: FONTS.regular,
    fontSize: 13,
    color: COLORS.darkGreenMuted,
    marginTop: 2,
  },
  logoutButton: {
    height: 34,
    paddingHorizontal: 14,
    borderRadius: 100,
    backgroundColor: 'rgba(239,68,68,0.12)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(239,68,68,0.35)',
  },
  logoutText: {
    fontFamily: FONTS.semibold,
    fontSize: 13,
    color: '#fca5a5',
  },
  greetingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 14,
    paddingTop: 6,
  },
  greetingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#34c46a',
    marginRight: 8,
  },
  greetingText: {
    fontFamily: FONTS.regular,
    fontSize: 13,
    color: COLORS.darkGreenText,
  },
  greetingName: {
    fontFamily: FONTS.bold,
    color: COLORS.white,
  },
});
