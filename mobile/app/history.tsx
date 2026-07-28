// ─────────────────────────────────────────────────────────────────────
// GEÇMİŞ ANALİZLERİM — app.py'deki gecmis_analiz_sayfasi()'nın mobil
// karşılığı: KPI'lar, bitki dağılımı, sağlık oranı, detaylı kayıt listesi
// ve toplu silme. Veri izolasyonu backend'de kullanıcı adına göre yapılır.
// ─────────────────────────────────────────────────────────────────────

import React, { useCallback, useMemo, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useFocusEffect } from 'expo-router';
import {
  fetchHistory,
  deleteHistoryRecords,
  type HistoryRecord,
} from '../src/services/api';
import { COLORS, FONTS, SHADOW_TINT } from '../src/constants/theme';
import { format, apiErrorText } from '../src/constants/i18n';
import { useLanguage } from '../src/context/LanguageContext';
import AppHeader from '../src/components/AppHeader';
import BottomNav from '../src/components/BottomNav';

export default function HistoryScreen() {
  const { lang, T } = useLanguage();
  const params = useLocalSearchParams<{ username?: string }>();
  const username = params.username || '';

  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [selectMode, setSelectMode] = useState(false);
  const [selected, setSelected] = useState<number[]>([]);

  // ─── Veri çekme ────────────────────────────────────────────────────
  const load = useCallback(
    async (isRefresh = false) => {
      if (!username) {
        setError(T.err_session);
        setLoading(false);
        return;
      }
      isRefresh ? setRefreshing(true) : setLoading(true);
      try {
        const result = await fetchHistory(username);
        if (result.success) {
          setRecords(result.records || []);
          setError('');
        } else {
          setError(T.err_db_read);
        }
      } catch (err: any) {
        setError(apiErrorText(err?.code, T, T.err_db_read));
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [username, T]
  );

  // Sayfaya her dönüşte tazele — yeni analiz sonrası liste güncel kalsın.
  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  // ─── Özet hesaplar (app.py'deki pandas mantığının karşılığı) ───────
  const summary = useMemo(() => {
    const total = records.length;

    const isHealthyText = (text: string) => {
      const t = (text || '').toLowerCase();
      return t.includes('sağlıklı') || t.includes('healthy');
    };
    const isNoDetection = (text: string) =>
      (text || '').toLowerCase().includes('tespit edilemedi');

    // En sık hastalık — "Sağlıklı" ve "Tespit Edilemedi" hariç
    const counts = new Map<string, number>();
    records.forEach((r) => {
      const value = r.hastalik_durumu || '';
      if (!value || isHealthyText(value) || isNoDetection(value)) return;
      counts.set(value, (counts.get(value) || 0) + 1);
    });
    let mostCommon = T.no_disease;
    let max = 0;
    counts.forEach((count, name) => {
      if (count > max) {
        max = count;
        mostCommon = name;
      }
    });

    // Bitki türü dağılımı
    const plantCounts = new Map<string, number>();
    records.forEach((r) => {
      const value = r.bitki_turu || (lang === 'tr' ? 'Bilinmiyor' : 'Unknown');
      plantCounts.set(value, (plantCounts.get(value) || 0) + 1);
    });
    const plants = [...plantCounts.entries()]
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count);
    const plantMax = plants.length > 0 ? plants[0].count : 1;

    // Sağlıklı / enfekte oranı
    const healthy = records.filter((r) =>
      isHealthyText(r.hastalik_durumu)
    ).length;
    const infected = total - healthy;

    return { total, mostCommon, plants, plantMax, healthy, infected };
  }, [records, T, lang]);

  // ─── Seçim & silme ─────────────────────────────────────────────────
  const toggleSelect = (id: number) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const exitSelectMode = () => {
    setSelectMode(false);
    setSelected([]);
  };

  const confirmDelete = () => {
    if (selected.length === 0) return;
    Alert.alert(T.delete_title, format(T.delete_confirm, selected.length), [
      { text: T.cancel, style: 'cancel' },
      {
        text: T.delete_btn,
        style: 'destructive',
        onPress: async () => {
          try {
            const result = await deleteHistoryRecords(username, selected);
            if (result.success) {
              Alert.alert(T.delete_title, format(T.delete_ok, result.deleted));
              exitSelectMode();
              load(true);
            } else {
              Alert.alert(T.delete_title, T.delete_err);
            }
          } catch (err: any) {
            Alert.alert(T.delete_title, apiErrorText(err?.code, T, T.delete_err));
          }
        },
      },
    ]);
  };

  // Tarih biçimi: "2026-07-28 13:47:56" → "28.07.2026 13:47"
  const formatDate = (raw: string): string => {
    if (!raw) return '';
    const [datePart, timePart = ''] = raw.split(' ');
    const [y, m, d] = datePart.split('-');
    if (!y || !m || !d) return raw;
    const hhmm = timePart.slice(0, 5);
    return lang === 'tr'
      ? `${d}.${m}.${y} ${hhmm}`.trim()
      : `${m}/${d}/${y} ${hhmm}`.trim();
  };

  const healthTotal = summary.healthy + summary.infected;
  const healthyPct =
    healthTotal > 0 ? Math.round((summary.healthy / healthTotal) * 100) : 0;

  return (
    <SafeAreaView style={styles.container}>
      <AppHeader username={username} />

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => load(true)}
            colors={[COLORS.primary]}
            tintColor={COLORS.primary}
          />
        }
      >
        {/* ── Sayfa başlığı ── */}
        <View style={styles.pageHead}>
          <View style={styles.tag}>
            <Text style={styles.tagText}>{T.hist_tag}</Text>
          </View>
          <Text style={styles.pageTitle}>{T.hist_title}</Text>
          <Text style={styles.pageDesc}>{T.hist_desc}</Text>
        </View>

        {loading ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" color={COLORS.primary} />
            <Text style={styles.loadingText}>{T.hist_loading}</Text>
          </View>
        ) : error !== '' ? (
          <View style={styles.errorCard}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        ) : records.length === 0 ? (
          <View style={styles.infoCard}>
            <Text style={styles.infoText}>{T.info_empty}</Text>
          </View>
        ) : (
          <>
            {/* ── KPI'lar ── */}
            <View style={styles.kpiRow}>
              <View style={styles.kpiCard}>
                <Text style={styles.kpiLabel}>{T.kpi_total}</Text>
                <Text style={styles.kpiValue}>{summary.total}</Text>
              </View>
              <View style={styles.kpiCard}>
                <Text style={styles.kpiLabel}>{T.kpi_common}</Text>
                <Text style={styles.kpiDisease} numberOfLines={3}>
                  {summary.mostCommon}
                </Text>
              </View>
            </View>

            {/* ── Bitki türü dağılımı (yatay bar) ── */}
            <View style={styles.card}>
              <Text style={styles.cardTitle}>{T.chart1_t}</Text>
              <Text style={styles.cardDesc}>{T.chart1_d}</Text>
              {summary.plants.map((p) => (
                <View key={p.name} style={styles.barRow}>
                  <Text style={styles.barLabel} numberOfLines={1}>
                    {p.name}
                  </Text>
                  <View style={styles.barTrack}>
                    <View
                      style={[
                        styles.barFill,
                        { width: `${(p.count / summary.plantMax) * 100}%` },
                      ]}
                    />
                  </View>
                  <Text style={styles.barValue}>{p.count}</Text>
                </View>
              ))}
            </View>

            {/* ── Sağlık durumu oranı ── */}
            <View style={styles.card}>
              <Text style={styles.cardTitle}>{T.chart2_t}</Text>
              <Text style={styles.cardDesc}>{T.chart2_d}</Text>

              <View style={styles.ratioTrack}>
                <View
                  style={[styles.ratioHealthy, { flex: summary.healthy || 0 }]}
                />
                <View
                  style={[styles.ratioInfected, { flex: summary.infected || 0 }]}
                />
              </View>

              <View style={styles.legendRow}>
                <View style={styles.legendItem}>
                  <View
                    style={[styles.legendDot, { backgroundColor: COLORS.primary }]}
                  />
                  <Text style={styles.legendText}>
                    {T.status_healthy} · {summary.healthy} (
                    {lang === 'tr' ? `%${healthyPct}` : `${healthyPct}%`})
                  </Text>
                </View>
                <View style={styles.legendItem}>
                  <View
                    style={[styles.legendDot, { backgroundColor: COLORS.red }]}
                  />
                  <Text style={styles.legendText}>
                    {T.status_infected} · {summary.infected} (
                    {lang === 'tr'
                      ? `%${100 - healthyPct}`
                      : `${100 - healthyPct}%`}
                    )
                  </Text>
                </View>
              </View>
            </View>

            {/* ── Detaylı kayıt listesi ── */}
            <View style={styles.card}>
              <View style={styles.tableHeadRow}>
                <View style={styles.tableHeadLeft}>
                  <Text style={styles.cardTitle}>{T.table_t}</Text>
                  <Text style={styles.cardDesc}>{T.table_d}</Text>
                </View>
                <TouchableOpacity
                  style={styles.selectButton}
                  onPress={() =>
                    selectMode ? exitSelectMode() : setSelectMode(true)
                  }
                  activeOpacity={0.7}
                >
                  <Text style={styles.selectButtonText}>
                    {selectMode ? T.select_cancel : T.select_mode}
                  </Text>
                </TouchableOpacity>
              </View>

              {records.map((rec) => {
                const isSelected = selected.includes(rec.islem_id);
                const healthy = (rec.hastalik_durumu || '')
                  .toLowerCase()
                  .match(/sağlıklı|healthy/);
                return (
                  <TouchableOpacity
                    key={rec.islem_id}
                    style={[styles.recordRow, isSelected && styles.recordRowSelected]}
                    activeOpacity={selectMode ? 0.7 : 1}
                    onPress={() => selectMode && toggleSelect(rec.islem_id)}
                  >
                    {selectMode && (
                      <View
                        style={[
                          styles.checkbox,
                          isSelected && styles.checkboxChecked,
                        ]}
                      >
                        {isSelected && <Text style={styles.checkMark}>✓</Text>}
                      </View>
                    )}
                    <View style={styles.recordBody}>
                      <Text style={styles.recordDate}>
                        {formatDate(rec.tarih)}
                      </Text>
                      <Text style={styles.recordPlant} numberOfLines={1}>
                        {rec.bitki_turu}
                      </Text>
                      <Text
                        style={[
                          styles.recordDisease,
                          { color: healthy ? COLORS.primaryText : COLORS.red },
                        ]}
                        numberOfLines={2}
                      >
                        {rec.hastalik_durumu}
                      </Text>
                    </View>
                  </TouchableOpacity>
                );
              })}

              {selectMode && (
                <>
                  <Text style={styles.selectedCount}>
                    {format(T.delete_count, selected.length)}
                  </Text>
                  <TouchableOpacity
                    style={[
                      styles.deleteButton,
                      selected.length === 0 && styles.deleteButtonDisabled,
                    ]}
                    onPress={confirmDelete}
                    disabled={selected.length === 0}
                    activeOpacity={0.85}
                  >
                    <Text style={styles.deleteButtonText}>{T.delete_btn}</Text>
                  </TouchableOpacity>
                </>
              )}
            </View>
          </>
        )}

        <View style={{ height: 20 }} />
      </ScrollView>

      <BottomNav active="history" username={username} />
    </SafeAreaView>
  );
}

// ─── Styles ──────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgPage,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },

  pageHead: {
    marginBottom: 14,
  },
  tag: {
    alignSelf: 'flex-start',
    backgroundColor: COLORS.successSoft,
    borderWidth: 1,
    borderColor: COLORS.successBorder,
    borderRadius: 100,
    paddingHorizontal: 12,
    paddingVertical: 4,
    marginBottom: 10,
  },
  tagText: {
    fontFamily: FONTS.semibold,
    fontSize: 10,
    letterSpacing: 1,
    color: COLORS.success,
  },
  pageTitle: {
    fontFamily: FONTS.extrabold,
    fontSize: 24,
    color: COLORS.textDark,
    letterSpacing: -0.5,
    marginBottom: 6,
  },
  pageDesc: {
    fontFamily: FONTS.regular,
    fontSize: 13.5,
    lineHeight: 20,
    color: COLORS.textSoft,
  },

  loadingBox: {
    alignItems: 'center',
    paddingVertical: 40,
    gap: 12,
  },
  loadingText: {
    fontFamily: FONTS.medium,
    fontSize: 13,
    color: COLORS.textSoft,
  },
  errorCard: {
    backgroundColor: COLORS.redSoft,
    borderWidth: 1,
    borderColor: COLORS.redBorder,
    borderRadius: 12,
    padding: 14,
  },
  errorText: {
    fontFamily: FONTS.medium,
    fontSize: 13,
    color: COLORS.red,
    lineHeight: 19,
  },
  infoCard: {
    backgroundColor: COLORS.primarySoft,
    borderWidth: 1,
    borderColor: COLORS.primaryBorder,
    borderRadius: 12,
    padding: 16,
  },
  infoText: {
    fontFamily: FONTS.medium,
    fontSize: 13.5,
    color: COLORS.primaryText,
    lineHeight: 20,
  },

  kpiRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  kpiCard: {
    flex: 1,
    backgroundColor: COLORS.bgCard,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 14,
    padding: 16,
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  kpiLabel: {
    fontFamily: FONTS.medium,
    fontSize: 11.5,
    color: COLORS.textSoft,
    marginBottom: 6,
  },
  kpiValue: {
    fontFamily: FONTS.extrabold,
    fontSize: 28,
    color: COLORS.textDark,
    letterSpacing: -1,
  },
  kpiDisease: {
    fontFamily: FONTS.semibold,
    fontSize: 13,
    color: COLORS.red,
    lineHeight: 18,
  },

  card: {
    backgroundColor: COLORS.bgCard,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  cardTitle: {
    fontFamily: FONTS.bold,
    fontSize: 15,
    color: COLORS.textDark,
    letterSpacing: -0.2,
  },
  cardDesc: {
    fontFamily: FONTS.medium,
    fontSize: 11.5,
    color: COLORS.textMuted,
    marginTop: 2,
    marginBottom: 12,
  },

  barRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  barLabel: {
    width: 96,
    fontFamily: FONTS.medium,
    fontSize: 12,
    color: COLORS.textMid,
  },
  barTrack: {
    flex: 1,
    height: 18,
    backgroundColor: COLORS.borderSoft,
    borderRadius: 6,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: 6,
  },
  barValue: {
    width: 26,
    textAlign: 'right',
    fontFamily: FONTS.bold,
    fontSize: 12,
    color: COLORS.textDark,
  },

  ratioTrack: {
    flexDirection: 'row',
    height: 22,
    borderRadius: 8,
    overflow: 'hidden',
    backgroundColor: COLORS.borderSoft,
  },
  ratioHealthy: {
    backgroundColor: COLORS.primary,
  },
  ratioInfected: {
    backgroundColor: COLORS.red,
  },
  legendRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 14,
    marginTop: 10,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  legendDot: {
    width: 9,
    height: 9,
    borderRadius: 5,
  },
  legendText: {
    fontFamily: FONTS.medium,
    fontSize: 12,
    color: COLORS.textMid,
  },

  tableHeadRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: 10,
  },
  tableHeadLeft: {
    flex: 1,
  },
  selectButton: {
    borderWidth: 1,
    borderColor: COLORS.primaryBorder,
    backgroundColor: COLORS.primarySoft,
    borderRadius: 100,
    paddingHorizontal: 14,
    paddingVertical: 6,
  },
  selectButtonText: {
    fontFamily: FONTS.semibold,
    fontSize: 12,
    color: COLORS.primaryText,
  },

  recordRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    borderTopWidth: 1,
    borderTopColor: COLORS.borderSoft,
    paddingVertical: 11,
  },
  recordRowSelected: {
    backgroundColor: COLORS.primarySoft,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 1.5,
    borderColor: COLORS.inputBorder,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxChecked: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  checkMark: {
    color: COLORS.white,
    fontSize: 13,
    fontFamily: FONTS.bold,
  },
  recordBody: {
    flex: 1,
  },
  recordDate: {
    fontFamily: FONTS.medium,
    fontSize: 11.5,
    color: COLORS.textMuted,
  },
  recordPlant: {
    fontFamily: FONTS.bold,
    fontSize: 14,
    color: COLORS.textDark,
    marginTop: 1,
  },
  recordDisease: {
    fontFamily: FONTS.medium,
    fontSize: 12.5,
    marginTop: 1,
    lineHeight: 17,
  },

  selectedCount: {
    fontFamily: FONTS.medium,
    fontSize: 12.5,
    color: COLORS.textSoft,
    marginTop: 12,
    marginBottom: 8,
    textAlign: 'center',
  },
  deleteButton: {
    backgroundColor: COLORS.red,
    borderRadius: 10,
    height: 46,
    justifyContent: 'center',
    alignItems: 'center',
  },
  deleteButtonDisabled: {
    opacity: 0.45,
  },
  deleteButtonText: {
    fontFamily: FONTS.bold,
    fontSize: 14.5,
    color: COLORS.white,
  },
});
