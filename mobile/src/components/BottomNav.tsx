// ─────────────────────────────────────────────────────────────────────
// Alt navigasyon — app.py'deki koyu yeşil sidebar menüsünün mobil
// karşılığı. Aktif satır dolu yeşil vurgu alır, pasif satırlar şeffaftır.
// ─────────────────────────────────────────────────────────────────────

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { COLORS, FONTS } from '../constants/theme';
import { useLanguage } from '../context/LanguageContext';

export type NavKey = 'home' | 'history';

type Props = {
  active: NavKey;
  /** Sayfalar arası taşınan aktif kullanıcı adı */
  username: string;
};

export default function BottomNav({ active, username }: Props) {
  const router = useRouter();
  const { T } = useLanguage();

  const go = (key: NavKey) => {
    if (key === active) return;
    router.replace({
      pathname: key === 'home' ? '/home' : '/history',
      params: { username },
    });
  };

  const items: { key: NavKey; label: string; icon: string }[] = [
    { key: 'home', label: T.nav_home, icon: '🌿' },
    { key: 'history', label: T.nav_history, icon: '📊' },
  ];

  return (
    <View style={styles.bar}>
      {items.map((item) => {
        const isActive = item.key === active;
        return (
          <TouchableOpacity
            key={item.key}
            style={[styles.item, isActive && styles.itemActive]}
            onPress={() => go(item.key)}
            activeOpacity={0.8}
          >
            <Text style={styles.icon}>{item.icon}</Text>
            <Text
              style={[styles.label, isActive && styles.labelActive]}
              numberOfLines={1}
            >
              {item.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  bar: {
    flexDirection: 'row',
    gap: 8,
    backgroundColor: COLORS.darkGreenMid,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.06)',
    paddingHorizontal: 12,
    paddingTop: 8,
    paddingBottom: 10,
  },
  item: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 7,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'transparent',
    paddingVertical: 10,
    paddingHorizontal: 8,
  },
  itemActive: {
    backgroundColor: COLORS.darkGreenActive,
    borderColor: COLORS.darkGreenActive,
  },
  icon: {
    fontSize: 14,
  },
  label: {
    flexShrink: 1,
    fontFamily: FONTS.medium,
    fontSize: 12.5,
    color: COLORS.darkGreenText,
  },
  labelActive: {
    fontFamily: FONTS.semibold,
    color: COLORS.white,
  },
});
