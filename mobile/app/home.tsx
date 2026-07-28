import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Image,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import {
  analyzeImage,
  type AnalysisResult,
  type Disease,
} from '../src/services/api';
import { COLORS, FONTS, SHADOW_TINT, riskColor } from '../src/constants/theme';
import { DEFAULT_CONFIDENCE } from '../src/constants/config';
import { format, apiErrorText } from '../src/constants/i18n';
import { useLanguage } from '../src/context/LanguageContext';
import AppHeader from '../src/components/AppHeader';
import BottomNav from '../src/components/BottomNav';
import ConfidenceSlider from '../src/components/ConfidenceSlider';

export default function HomeScreen() {
  const { lang, T } = useLanguage();
  const params = useLocalSearchParams<{ username?: string }>();
  const username = params.username || (lang === 'tr' ? 'Kullanıcı' : 'User');

  const [imageUri, setImageUri] = useState<string | null>(null);
  const [resultImageBase64, setResultImageBase64] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [confidence, setConfidence] = useState<number>(DEFAULT_CONFIDENCE);

  // ─── Camera ──────────────────────────────────────────────────────

  const pickFromCamera = useCallback(async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(T.perm_title, T.perm_camera, [{ text: T.ok }]);
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.85,
      });

      if (!result.canceled && result.assets[0]) {
        setImageUri(result.assets[0].uri);
        setAnalysisResult(null);
        setResultImageBase64(null);
        setError('');
      }
    } catch (err) {
      setError(T.err_camera);
    }
  }, [T]);

  // ─── Gallery ─────────────────────────────────────────────────────

  const pickFromGallery = useCallback(async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(T.perm_title, T.perm_gallery, [{ text: T.ok }]);
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.85,
      });

      if (!result.canceled && result.assets[0]) {
        setImageUri(result.assets[0].uri);
        setAnalysisResult(null);
        setResultImageBase64(null);
        setError('');
      }
    } catch (err) {
      setError(T.err_gallery);
    }
  }, [T]);

  // ─── Analyze ─────────────────────────────────────────────────────

  const handleAnalyze = useCallback(async () => {
    if (!imageUri) return;

    setLoading(true);
    setError('');
    setAnalysisResult(null);
    setResultImageBase64(null);

    try {
      // Kullanıcı adı ve dil gönderilir → sonuç analiz_gecmisi'ne kaydedilir.
      const result = await analyzeImage(
        imageUri,
        confidence,
        undefined,
        params.username,
        lang
      );
      setAnalysisResult(result);
      // API'den dönen kutucuklu görselin TAM data URI'sini (data:image/jpeg;base64,...)
      // olduğu gibi sakla; ekrana basarken tekrar önek eklenmez.
      const boxedImage = result.image_base64 || result.result_image_base64;
      if (boxedImage) {
        setResultImageBase64(boxedImage);
      }
    } catch (err: any) {
      setError(
        apiErrorText(
          err?.code,
          T,
          lang === 'tr' ? err?.message : T.err_analyze
        )
      );
    } finally {
      setLoading(false);
    }
  }, [imageUri, T]);

  // ─── Reset ───────────────────────────────────────────────────────

  const handleReset = useCallback(() => {
    setImageUri(null);
    setResultImageBase64(null);
    setAnalysisResult(null);
    setError('');
  }, []);

  // Çıkış işlemi artık ortak AppHeader bileşeninde.

  // ─── Helpers ─────────────────────────────────────────────────────

  const getRiskColor = riskColor;

  const getRiskLabel = (score: number): string => {
    if (score < 30) return T.risk_low;
    if (score < 60) return T.risk_mid;
    return T.risk_high;
  };

  const summary = analysisResult?.summary;

  // Seçili dile göre veri alanı: API hem TR hem EN karşılıkları döndürüyor.
  const isTR = lang === 'tr';
  const plantTypes = summary
    ? isTR
      ? summary.plant_types_tr
      : summary.plant_types
    : [];
  // Yüzde biçimi: TR'de "%94", EN'de "94%"
  const pct = (value: number): string =>
    isTR ? `%${Math.round(value)}` : `${Math.round(value)}%`;
  // Tedavi metinleri Firestore'da TR/EN olarak ayrı tutuluyor.
  const treatmentOf = (disease: Disease) =>
    (isTR ? disease.treatment_tr : disease.treatment_en) ||
    ({ ilac: '', sonuc: '', ekonomi: '' } as Disease['treatment_tr']);

  // ─── Render ──────────────────────────────────────────────────────

  return (
    <SafeAreaView style={styles.container}>
      <AppHeader username={username} />

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* ── HERO — app.py ana sayfasındaki tanıtım kartı ──────── */}
        <View style={styles.hero}>
          <View style={styles.heroBadge}>
            <Text style={styles.heroBadgeText}>{T.nav_powered}</Text>
          </View>
          <Text style={styles.heroTitle}>{T.main_title}</Text>
          <Text style={styles.heroDesc}>{T.main_desc}</Text>
        </View>

        {/* ── KPI KARTLARI (app.py st.metric dörtlüsü) ──────────── */}
        <View style={styles.kpiGrid}>
          {[
            { v: isTR ? '%94' : '94%', l: T.kpi_acc, d: T.kpi_acc_d },
            { v: isTR ? '<1 sn' : '<1 s', l: T.kpi_time, d: T.kpi_time_d },
            { v: '29', l: T.kpi_dis, d: T.kpi_dis_d },
            { v: '13', l: T.kpi_plants, d: T.kpi_plants_d },
          ].map((kpi) => (
            <View key={kpi.l} style={styles.kpiCard}>
              <Text style={styles.kpiValue}>{kpi.v}</Text>
              <Text style={styles.kpiLabel}>{kpi.l}</Text>
              <Text style={styles.kpiHint}>{kpi.d}</Text>
            </View>
          ))}
        </View>

        {/* ── GÜVEN EŞİĞİ — app.py'deki st.slider'ın birebir karşılığı ── */}
        <View style={styles.sectionCard}>
          <View style={styles.confHeader}>
            <Text style={styles.sectionTitle}>{T.conf_label}</Text>
            <View style={styles.confValueBadge}>
              <Text style={styles.confValueText}>{confidence.toFixed(2)}</Text>
            </View>
          </View>
          <ConfidenceSlider
            value={confidence}
            onChange={setConfidence}
            min={0}
            max={1}
            step={0.01}
            disabled={loading}
          />
          <Text style={styles.confHint}>{T.conf_hint}</Text>
        </View>

        {/* ── Photo Section ─────────────────────────────────────── */}
        <View style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>{T.sec_photo}</Text>
          <View style={styles.photoArea}>
            {resultImageBase64 ? (
              // Analiz sonrası: API'den dönen kutucuklu (bounding box) görsel.
              // resultImageBase64 zaten "data:image/jpeg;base64,..." önekini içerir.
              <Image
                source={{ uri: resultImageBase64 }}
                style={styles.photoImage}
                resizeMode="contain"
              />
            ) : imageUri ? (
              // Analiz öncesi: kullanıcının galeriden/kameradan seçtiği orijinal fotoğraf
              <Image
                source={{ uri: imageUri }}
                style={styles.photoImage}
                resizeMode="cover"
              />
            ) : (
              <View style={styles.photoPlaceholder}>
                <Text style={styles.placeholderText}>{T.photo_ph}</Text>
                <Text style={styles.placeholderHint}>{T.photo_hint}</Text>
              </View>
            )}
          </View>
        </View>

        {/* ── Action Buttons ────────────────────────────────────── */}
        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={[styles.actionButton, styles.cameraButton]}
            onPress={pickFromCamera}
            activeOpacity={0.8}
            disabled={loading}
          >
            <Text style={styles.actionButtonText}>{T.btn_camera}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.galleryButton]}
            onPress={pickFromGallery}
            activeOpacity={0.8}
            disabled={loading}
          >
            <Text style={styles.actionButtonText}>{T.btn_gallery}</Text>
          </TouchableOpacity>
        </View>

        {/* Analyze Button */}
        <TouchableOpacity
          style={[
            styles.analyzeButton,
            (!imageUri || loading) && styles.analyzeButtonDisabled,
          ]}
          onPress={handleAnalyze}
          disabled={!imageUri || loading}
          activeOpacity={0.8}
        >
          {loading ? (
            <View style={styles.loadingRow}>
              <ActivityIndicator size="small" color={COLORS.white} />
              <Text style={styles.analyzeButtonText}>
                {'  '}
                {T.analyzing}
              </Text>
            </View>
          ) : (
            <Text style={styles.analyzeButtonText}>{T.btn_analyze}</Text>
          )}
        </TouchableOpacity>

        {/* ── Error Message ─────────────────────────────────────── */}
        {error !== '' && (
          <View style={styles.errorCard}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {/* ── Results ───────────────────────────────────────────── */}
        {analysisResult && summary && (
          <View style={styles.resultsContainer}>
            <View style={styles.resultsDivider}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>{T.results_title}</Text>
              <View style={styles.dividerLine} />
            </View>

            {/* Plant Type Card */}
            <View style={styles.resultCard}>
              <View style={styles.resultCardHeader}>
                <Text style={styles.resultCardTitle}>{T.res_plant}</Text>
              </View>
              <View style={styles.plantChipsRow}>
                {plantTypes.length > 0 ? (
                  plantTypes.map((plant, idx) => (
                    <View key={idx} style={styles.plantChip}>
                      <Text style={styles.plantChipText}>{plant}</Text>
                    </View>
                  ))
                ) : (
                  <Text style={styles.noDataText}>{T.no_plant}</Text>
                )}
              </View>
            </View>

            {/* Health Status */}
            <View style={styles.resultCard}>
              <View style={styles.resultCardHeader}>
                <Text style={styles.resultCardTitle}>{T.res_health}</Text>
              </View>
              <View
                style={[
                  styles.healthBadge,
                  {
                    backgroundColor: summary.is_healthy
                      ? COLORS.successSoft
                      : COLORS.redSoft,
                    borderColor: summary.is_healthy
                      ? COLORS.successBorder
                      : COLORS.redBorder,
                  },
                ]}
              >
                <Text
                  style={[
                    styles.healthBadgeText,
                    {
                      color: summary.is_healthy ? COLORS.success : COLORS.red,
                    },
                  ]}
                >
                  {summary.is_healthy
                    ? T.healthy
                    : format(T.diseases_found, summary.disease_count)}
                </Text>
              </View>
            </View>

            {/* Risk Score */}
            <View style={styles.resultCard}>
              <View style={styles.resultCardHeader}>
                <Text style={styles.resultCardTitle}>{T.risk_label}</Text>
              </View>
              <View style={styles.riskScoreContainer}>
                <Text
                  style={[
                    styles.riskScoreValue,
                    { color: getRiskColor(summary.risk_score) },
                  ]}
                >
                  {pct(summary.risk_score)}
                </Text>
                <View
                  style={[
                    styles.riskLabel,
                    {
                      backgroundColor: `${getRiskColor(summary.risk_score)}18`,
                      borderColor: `${getRiskColor(summary.risk_score)}40`,
                    },
                  ]}
                >
                  <Text
                    style={[
                      styles.riskLabelText,
                      { color: getRiskColor(summary.risk_score) },
                    ]}
                  >
                    {getRiskLabel(summary.risk_score)}
                  </Text>
                </View>
              </View>
              {/* Risk Bar */}
              <View style={styles.riskBarBackground}>
                <View
                  style={[
                    styles.riskBarFill,
                    {
                      width: `${Math.min(summary.risk_score, 100)}%`,
                      backgroundColor: getRiskColor(summary.risk_score),
                    },
                  ]}
                />
              </View>
            </View>

            {/* Detection Details */}
            {analysisResult.detections.length > 0 && (
              <View style={styles.resultCard}>
                <View style={styles.resultCardHeader}>
                  <Text style={styles.resultCardTitle}>{T.res_detections}</Text>
                </View>
                {analysisResult.detections.map((det, idx) => (
                  <View key={idx} style={styles.detectionRow}>
                    <View style={styles.detectionLeft}>
                      <View style={styles.detectionDot} />
                      <Text style={styles.detectionName}>
                        {isTR
                          ? det.class_name_tr || det.class_name
                          : det.class_name}
                      </Text>
                    </View>
                    <View style={styles.confidenceBadge}>
                      <Text style={styles.confidenceText}>
                        {pct(det.confidence * 100)}
                      </Text>
                    </View>
                  </View>
                ))}
              </View>
            )}

            {/* Disease Cards */}
            {summary.diseases.length > 0 && (
              <>
                <View style={styles.diseaseSectionHeader}>
                  <Text style={styles.diseaseSectionTitle}>
                    {T.disease_section}
                  </Text>
                </View>

                {summary.diseases.map((disease, idx) => (
                  <View key={idx} style={styles.diseaseCard}>
                    <View style={styles.diseaseHeader}>
                      <View style={styles.diseaseNumberBadge}>
                        <Text style={styles.diseaseNumber}>{idx + 1}</Text>
                      </View>
                      <View style={styles.diseaseNameContainer}>
                        <Text style={styles.diseaseName}>
                          {isTR ? disease.name_tr || disease.name : disease.name}
                        </Text>
                        {isTR &&
                          disease.name_tr &&
                          disease.name !== disease.name_tr && (
                            <Text style={styles.diseaseNameEn}>
                              {disease.name}
                            </Text>
                          )}
                      </View>
                    </View>

                    {/* Treatment: Medicine */}
                    <View
                      style={[
                        styles.treatmentItem,
                        { borderLeftColor: COLORS.success },
                      ]}
                    >
                      <Text style={styles.treatmentLabel}>{T.lbl_ilac}</Text>
                      <Text style={styles.treatmentText}>
                        {treatmentOf(disease).ilac || T.no_info}
                      </Text>
                    </View>

                    {/* Treatment: Agronomic */}
                    <View
                      style={[
                        styles.treatmentItem,
                        { borderLeftColor: COLORS.amber },
                      ]}
                    >
                      <Text style={styles.treatmentLabel}>{T.lbl_sonuc}</Text>
                      <Text style={styles.treatmentText}>
                        {treatmentOf(disease).sonuc || T.no_info}
                      </Text>
                    </View>

                    {/* Treatment: Financial */}
                    <View
                      style={[
                        styles.treatmentItem,
                        { borderLeftColor: COLORS.info },
                      ]}
                    >
                      <Text style={styles.treatmentLabel}>{T.lbl_ekonomi}</Text>
                      <Text style={styles.treatmentText}>
                        {treatmentOf(disease).ekonomi || T.no_info}
                      </Text>
                    </View>
                  </View>
                ))}
              </>
            )}

            {/* New Analysis Button */}
            <TouchableOpacity
              style={styles.resetButton}
              onPress={handleReset}
              activeOpacity={0.8}
            >
              <Text style={styles.resetButtonText}>{T.btn_new_analysis}</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* ── NASIL ÇALIŞIR? — app.py'deki üç adım bölümü ───────── */}
        {!analysisResult && (
          <View style={styles.sectionCard}>
            <Text style={styles.sectionTitle}>{T.how_title}</Text>
            {[
              { n: '1', t: T.step1_t, d: T.step1_d },
              { n: '2', t: T.step2_t, d: T.step2_d },
              { n: '3', t: T.step3_t, d: T.step3_d },
            ].map((step) => (
              <View key={step.n} style={styles.stepRow}>
                <View style={styles.stepNum}>
                  <Text style={styles.stepNumText}>{step.n}</Text>
                </View>
                <View style={styles.stepBody}>
                  <Text style={styles.stepTitle}>{step.t}</Text>
                  <Text style={styles.stepDesc}>{step.d}</Text>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Bottom Spacer */}
        <View style={{ height: 20 }} />
      </ScrollView>

      <BottomNav active="home" username={username} />
    </SafeAreaView>
  );
}

// ─── Styles ──────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgPage,
  },

  // Başlık ortak bileşende (src/components/AppHeader.tsx)

  // ── HERO — app.py ana sayfasındaki tanıtım kartı ──
  hero: {
    backgroundColor: COLORS.bgCard,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 16,
    padding: 18,
    marginBottom: 12,
  },
  heroBadge: {
    alignSelf: 'flex-start',
    backgroundColor: COLORS.successSoft,
    borderWidth: 1,
    borderColor: COLORS.successBorder,
    borderRadius: 100,
    paddingHorizontal: 12,
    paddingVertical: 4,
    marginBottom: 10,
  },
  heroBadgeText: {
    fontFamily: FONTS.semibold,
    fontSize: 10,
    letterSpacing: 0.8,
    color: COLORS.success,
  },
  heroTitle: {
    fontFamily: FONTS.extrabold,
    fontSize: 22,
    lineHeight: 28,
    color: COLORS.textDark,
    letterSpacing: -0.5,
    marginBottom: 8,
  },
  heroDesc: {
    fontFamily: FONTS.regular,
    fontSize: 13.5,
    lineHeight: 20,
    color: COLORS.textSoft,
  },

  // ── KPI kartları ──
  kpiGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 12,
  },
  kpiCard: {
    flexBasis: '47.5%',
    flexGrow: 1,
    backgroundColor: COLORS.bgCard,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 14,
    padding: 14,
  },
  kpiValue: {
    fontFamily: FONTS.extrabold,
    fontSize: 22,
    color: COLORS.primaryText,
    letterSpacing: -0.6,
  },
  kpiLabel: {
    fontFamily: FONTS.semibold,
    fontSize: 12.5,
    color: COLORS.textDark,
    marginTop: 2,
  },
  kpiHint: {
    fontFamily: FONTS.medium,
    fontSize: 11,
    color: COLORS.textMuted,
    marginTop: 1,
  },

  // ── Güven eşiği kaydırıcısı ──
  confHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  confValueBadge: {
    backgroundColor: COLORS.primarySoft,
    borderWidth: 1,
    borderColor: COLORS.primaryBorder,
    borderRadius: 100,
    paddingHorizontal: 12,
    paddingVertical: 4,
    minWidth: 58,
    alignItems: 'center',
  },
  confValueText: {
    fontFamily: FONTS.bold,
    fontSize: 13.5,
    color: COLORS.primaryText,
  },
  confHint: {
    fontFamily: FONTS.medium,
    fontSize: 11.5,
    lineHeight: 17,
    color: COLORS.textSoft,
    marginTop: 10,
  },

  // ── Üç adım bölümü ──
  stepRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 12,
  },
  stepNum: {
    width: 30,
    height: 30,
    borderRadius: 9,
    backgroundColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  stepNumText: {
    fontFamily: FONTS.extrabold,
    fontSize: 14,
    color: COLORS.white,
  },
  stepBody: {
    flex: 1,
  },
  stepTitle: {
    fontFamily: FONTS.bold,
    fontSize: 14,
    color: COLORS.textDark,
  },
  stepDesc: {
    fontFamily: FONTS.regular,
    fontSize: 12.5,
    lineHeight: 18,
    color: COLORS.textSoft,
    marginTop: 2,
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
    // koyu yeşil başlık üzerinde parlak yeşil nokta
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

  // Scroll
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },

  // Section Card
  sectionCard: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  sectionTitle: {
    fontFamily: FONTS.bold,
    fontSize: 15,
    color: COLORS.textMid,
    marginBottom: 12,
  },

  // Photo Area
  photoArea: {
    height: 300,
    borderRadius: 14,
    overflow: 'hidden',
    backgroundColor: COLORS.inputBg,
  },
  photoImage: {
    width: '100%',
    height: '100%',
  },
  photoPlaceholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: COLORS.primaryBorder,
    borderStyle: 'dashed',
    borderRadius: 14,
  },
  placeholderText: {
    fontFamily: FONTS.semibold,
    fontSize: 15,
    color: COLORS.textSoft,
    marginBottom: 4,
  },
  placeholderHint: {
    fontFamily: FONTS.regular,
    fontSize: 12,
    color: COLORS.textMuted,
  },

  // Action Buttons
  buttonRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 10,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 52,
    borderRadius: 12,
    gap: 8,
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 2,
  },
  cameraButton: {
    backgroundColor: COLORS.bgCard,
    borderWidth: 1.5,
    borderColor: COLORS.primary,
  },
  galleryButton: {
    backgroundColor: COLORS.bgCard,
    borderWidth: 1.5,
    borderColor: COLORS.primary,
  },
  actionButtonText: {
    fontFamily: FONTS.bold,
    fontSize: 15,
    color: COLORS.primaryText,
  },

  // Analyze Button
  analyzeButton: {
    backgroundColor: COLORS.primary,
    height: 54,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.28,
    shadowRadius: 12,
    elevation: 5,
  },
  analyzeButtonDisabled: {
    backgroundColor: '#b9c7bf',
    shadowOpacity: 0,
    elevation: 0,
  },
  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  analyzeButtonText: {
    fontFamily: FONTS.extrabold,
    fontSize: 17,
    color: COLORS.white,
    letterSpacing: 0.2,
  },

  // Error
  errorCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.redSoft,
    borderRadius: 14,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.redBorder,
  },
  errorText: {
    flex: 1,
    fontFamily: FONTS.medium,
    fontSize: 13,
    color: COLORS.red,
    lineHeight: 19,
  },

  // Results Container
  resultsContainer: {
    marginTop: 4,
  },
  resultsDivider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 10,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: COLORS.border,
  },
  dividerText: {
    fontFamily: FONTS.bold,
    fontSize: 15,
    color: COLORS.textMid,
  },

  // Result Card
  resultCard: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 16,
    padding: 18,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: COLORS.border,
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  resultCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
    gap: 8,
  },
  resultCardTitle: {
    fontFamily: FONTS.bold,
    fontSize: 15,
    color: COLORS.textMid,
  },

  // Plant Chips
  plantChipsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  plantChip: {
    backgroundColor: COLORS.successSoft,
    borderRadius: 100,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: COLORS.successBorder,
  },
  plantChipText: {
    fontFamily: FONTS.semibold,
    fontSize: 14,
    color: COLORS.success,
  },
  noDataText: {
    fontFamily: FONTS.regular,
    fontSize: 13,
    color: COLORS.textMuted,
    fontStyle: 'italic',
  },

  // Health Badge
  healthBadge: {
    borderRadius: 12,
    paddingHorizontal: 18,
    paddingVertical: 12,
    alignItems: 'center',
    borderWidth: 1,
  },
  healthBadgeText: {
    fontFamily: FONTS.bold,
    fontSize: 15,
  },

  // Risk Score
  riskScoreContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    marginBottom: 14,
  },
  riskScoreValue: {
    fontFamily: FONTS.black,
    fontSize: 42,
    letterSpacing: -1,
  },
  riskLabel: {
    borderRadius: 100,
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderWidth: 1,
  },
  riskLabelText: {
    fontFamily: FONTS.bold,
    fontSize: 13,
  },
  riskBarBackground: {
    height: 8,
    backgroundColor: COLORS.borderSoft,
    borderRadius: 4,
    overflow: 'hidden',
  },
  riskBarFill: {
    height: '100%',
    borderRadius: 4,
  },

  // Detection Row
  detectionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderSoft,
  },
  detectionLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    gap: 10,
  },
  detectionDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: COLORS.primary,
  },
  detectionName: {
    fontFamily: FONTS.medium,
    fontSize: 14,
    color: COLORS.textMid,
    flex: 1,
  },
  confidenceBadge: {
    backgroundColor: COLORS.primarySoft,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  confidenceText: {
    fontFamily: FONTS.bold,
    fontSize: 13,
    color: COLORS.primaryText,
  },

  // Disease Section
  diseaseSectionHeader: {
    marginTop: 6,
    marginBottom: 12,
  },
  diseaseSectionTitle: {
    fontFamily: FONTS.extrabold,
    fontSize: 16,
    color: COLORS.textDark,
  },

  // Disease Card
  diseaseCard: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 16,
    padding: 18,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.red,
    shadowColor: SHADOW_TINT,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  diseaseHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 12,
  },
  diseaseNumberBadge: {
    width: 30,
    height: 30,
    borderRadius: 10,
    backgroundColor: COLORS.redSoft,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.redBorder,
  },
  diseaseNumber: {
    fontFamily: FONTS.extrabold,
    fontSize: 14,
    color: COLORS.red,
  },
  diseaseNameContainer: {
    flex: 1,
  },
  diseaseName: {
    fontFamily: FONTS.bold,
    fontSize: 16,
    color: COLORS.textDark,
  },
  diseaseNameEn: {
    fontFamily: FONTS.regular,
    fontSize: 12,
    color: COLORS.textMuted,
    marginTop: 2,
    fontStyle: 'italic',
  },

  // Treatment Items — renkli ince sol kenarlı, emojisiz blok
  treatmentItem: {
    marginBottom: 14,
    paddingLeft: 12,
    borderLeftWidth: 3,
    borderLeftColor: COLORS.border,
  },
  treatmentLabel: {
    fontFamily: FONTS.bold,
    fontSize: 12,
    color: COLORS.textSoft,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 3,
  },
  treatmentText: {
    fontFamily: FONTS.regular,
    fontSize: 14,
    color: COLORS.textMid,
    lineHeight: 20,
  },

  // Reset Button
  resetButton: {
    backgroundColor: COLORS.bgCard,
    height: 52,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
    borderWidth: 2,
    borderColor: COLORS.primary,
  },
  resetButtonText: {
    fontFamily: FONTS.bold,
    fontSize: 16,
    color: COLORS.primaryText,
  },
});
