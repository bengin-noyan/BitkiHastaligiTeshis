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
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import {
  analyzeImage,
  type AnalysisResult,
} from '../src/services/api';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

export default function HomeScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ username?: string }>();
  const username = params.username || 'Kullanıcı';

  const [imageUri, setImageUri] = useState<string | null>(null);
  const [resultImageBase64, setResultImageBase64] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // ─── Camera ──────────────────────────────────────────────────────

  const pickFromCamera = useCallback(async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(
          'İzin Gerekli',
          'Fotoğraf çekebilmek için kamera izni vermeniz gerekmektedir.',
          [{ text: 'Tamam' }]
        );
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
      setError('Kamera açılırken bir hata oluştu.');
    }
  }, []);

  // ─── Gallery ─────────────────────────────────────────────────────

  const pickFromGallery = useCallback(async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(
          'İzin Gerekli',
          'Galeriye erişebilmek için fotoğraf izni vermeniz gerekmektedir.',
          [{ text: 'Tamam' }]
        );
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
      setError('Galeri açılırken bir hata oluştu.');
    }
  }, []);

  // ─── Analyze ─────────────────────────────────────────────────────

  const handleAnalyze = useCallback(async () => {
    if (!imageUri) return;

    setLoading(true);
    setError('');
    setAnalysisResult(null);
    setResultImageBase64(null);

    try {
      const result = await analyzeImage(imageUri);
      setAnalysisResult(result);
      // API'den dönen kutucuklu görselin TAM data URI'sini (data:image/jpeg;base64,...)
      // olduğu gibi sakla; ekrana basarken tekrar önek eklenmez.
      const boxedImage = result.image_base64 || result.result_image_base64;
      if (boxedImage) {
        setResultImageBase64(boxedImage);
      }
    } catch (err: any) {
      setError(err.message || 'Analiz sırasında beklenmeyen bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  }, [imageUri]);

  // ─── Reset ───────────────────────────────────────────────────────

  const handleReset = useCallback(() => {
    setImageUri(null);
    setResultImageBase64(null);
    setAnalysisResult(null);
    setError('');
  }, []);

  // ─── Logout ──────────────────────────────────────────────────────

  const handleLogout = useCallback(() => {
    Alert.alert('Çıkış', 'Çıkış yapmak istediğinize emin misiniz?', [
      { text: 'İptal', style: 'cancel' },
      {
        text: 'Çıkış Yap',
        style: 'destructive',
        onPress: () => router.replace('/'),
      },
    ]);
  }, [router]);

  // ─── Helpers ─────────────────────────────────────────────────────

  const getRiskColor = (score: number): string => {
    if (score < 30) return '#22c55e';
    if (score < 60) return '#f59e0b';
    return '#ef4444';
  };

  const getRiskLabel = (score: number): string => {
    if (score < 30) return 'Düşük Risk';
    if (score < 60) return 'Orta Risk';
    return 'Yüksek Risk';
  };

  const summary = analysisResult?.summary;

  // ─── Render ──────────────────────────────────────────────────────

  return (
    <SafeAreaView style={styles.container}>
      {/* ── Header ────────────────────────────────────────────── */}
      <View style={styles.header}>
        <View style={styles.headerAccent} />
        <View style={styles.headerContent}>
          <View style={styles.headerLeft}>
            <Text style={styles.headerTitle}>🌿 Tarımsal Analiz</Text>
            <Text style={styles.headerSubtitle}>
              Yapay zekâ destekli bitki hastalığı teşhisi
            </Text>
          </View>
          <TouchableOpacity
            style={styles.logoutButton}
            onPress={handleLogout}
            activeOpacity={0.7}
          >
            <Text style={styles.logoutIcon}>🚪</Text>
          </TouchableOpacity>
        </View>
        {/* User greeting */}
        <View style={styles.greetingRow}>
          <View style={styles.greetingDot} />
          <Text style={styles.greetingText}>
            Hoş geldiniz, <Text style={styles.greetingName}>{username}</Text>
          </Text>
        </View>
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* ── Photo Section ─────────────────────────────────────── */}
        <View style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>📋 Fotoğraf</Text>
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
                <Text style={styles.placeholderIcon}>📸</Text>
                <Text style={styles.placeholderText}>
                  Yaprak fotoğrafı çekin veya seçin
                </Text>
                <Text style={styles.placeholderHint}>
                  Aşağıdaki butonları kullanarak başlayın
                </Text>
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
            <Text style={styles.actionButtonIcon}>📷</Text>
            <Text style={styles.actionButtonText}>Kamera</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.galleryButton]}
            onPress={pickFromGallery}
            activeOpacity={0.8}
            disabled={loading}
          >
            <Text style={styles.actionButtonIcon}>🖼️</Text>
            <Text style={styles.actionButtonText}>Galeri</Text>
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
              <ActivityIndicator size="small" color="#ffffff" />
              <Text style={styles.analyzeButtonText}>
                {'  '}Analiz ediliyor...
              </Text>
            </View>
          ) : (
            <Text style={styles.analyzeButtonText}>⚡ Analiz Et</Text>
          )}
        </TouchableOpacity>

        {/* ── Error Message ─────────────────────────────────────── */}
        {error !== '' && (
          <View style={styles.errorCard}>
            <Text style={styles.errorIcon}>⚠️</Text>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {/* ── Results ───────────────────────────────────────────── */}
        {analysisResult && summary && (
          <View style={styles.resultsContainer}>
            <View style={styles.resultsDivider}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>📊 Analiz Sonuçları</Text>
              <View style={styles.dividerLine} />
            </View>

            {/* Plant Type Card */}
            <View style={styles.resultCard}>
              <View style={styles.resultCardHeader}>
                <Text style={styles.resultCardIcon}>🌱</Text>
                <Text style={styles.resultCardTitle}>Tespit Edilen Bitki</Text>
              </View>
              <View style={styles.plantChipsRow}>
                {summary.plant_types_tr.length > 0 ? (
                  summary.plant_types_tr.map((plant, idx) => (
                    <View key={idx} style={styles.plantChip}>
                      <Text style={styles.plantChipText}>{plant}</Text>
                    </View>
                  ))
                ) : (
                  <Text style={styles.noDataText}>Bitki türü tespit edilemedi</Text>
                )}
              </View>
            </View>

            {/* Health Status */}
            <View style={styles.resultCard}>
              <View style={styles.resultCardHeader}>
                <Text style={styles.resultCardIcon}>
                  {summary.is_healthy ? '✅' : '🔴'}
                </Text>
                <Text style={styles.resultCardTitle}>Sağlık Durumu</Text>
              </View>
              <View
                style={[
                  styles.healthBadge,
                  {
                    backgroundColor: summary.is_healthy
                      ? '#f0fdf4'
                      : '#fef2f2',
                    borderColor: summary.is_healthy ? '#bbf7d0' : '#fecaca',
                  },
                ]}
              >
                <Text
                  style={[
                    styles.healthBadgeText,
                    {
                      color: summary.is_healthy ? '#16a34a' : '#dc2626',
                    },
                  ]}
                >
                  {summary.is_healthy
                    ? '🌿 Sağlıklı'
                    : `⚠️ ${summary.disease_count} Hastalık Tespit Edildi`}
                </Text>
              </View>
            </View>

            {/* Risk Score */}
            <View style={styles.resultCard}>
              <View style={styles.resultCardHeader}>
                <Text style={styles.resultCardIcon}>📈</Text>
                <Text style={styles.resultCardTitle}>Risk Skoru</Text>
              </View>
              <View style={styles.riskScoreContainer}>
                <Text
                  style={[
                    styles.riskScoreValue,
                    { color: getRiskColor(summary.risk_score) },
                  ]}
                >
                  %{Math.round(summary.risk_score)}
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
                  <Text style={styles.resultCardIcon}>🔍</Text>
                  <Text style={styles.resultCardTitle}>Tespit Detayları</Text>
                </View>
                {analysisResult.detections.map((det, idx) => (
                  <View key={idx} style={styles.detectionRow}>
                    <View style={styles.detectionLeft}>
                      <View style={styles.detectionDot} />
                      <Text style={styles.detectionName}>
                        {det.class_name_tr || det.class_name}
                      </Text>
                    </View>
                    <View style={styles.confidenceBadge}>
                      <Text style={styles.confidenceText}>
                        %{Math.round(det.confidence * 100)}
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
                    🦠 Hastalık Bilgileri ve Tedavi Önerileri
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
                          {disease.name_tr || disease.name}
                        </Text>
                        {disease.name_tr && disease.name !== disease.name_tr && (
                          <Text style={styles.diseaseNameEn}>
                            {disease.name}
                          </Text>
                        )}
                      </View>
                    </View>

                    {/* Treatment: Medicine */}
                    <View style={styles.treatmentItem}>
                      <View style={styles.treatmentIconBox}>
                        <Text style={styles.treatmentIcon}>💊</Text>
                      </View>
                      <View style={styles.treatmentContent}>
                        <Text style={styles.treatmentLabel}>Önerilen İlaç</Text>
                        <Text style={styles.treatmentText}>
                          {disease.treatment_tr?.ilac || 'Bilgi mevcut değil'}
                        </Text>
                      </View>
                    </View>

                    {/* Treatment: Agronomic */}
                    <View style={styles.treatmentItem}>
                      <View
                        style={[
                          styles.treatmentIconBox,
                          { backgroundColor: '#fef3c7' },
                        ]}
                      >
                        <Text style={styles.treatmentIcon}>🌾</Text>
                      </View>
                      <View style={styles.treatmentContent}>
                        <Text style={styles.treatmentLabel}>
                          Zirai Beklenti
                        </Text>
                        <Text style={styles.treatmentText}>
                          {disease.treatment_tr?.sonuc || 'Bilgi mevcut değil'}
                        </Text>
                      </View>
                    </View>

                    {/* Treatment: Financial */}
                    <View style={styles.treatmentItem}>
                      <View
                        style={[
                          styles.treatmentIconBox,
                          { backgroundColor: '#e0f2fe' },
                        ]}
                      >
                        <Text style={styles.treatmentIcon}>💰</Text>
                      </View>
                      <View style={styles.treatmentContent}>
                        <Text style={styles.treatmentLabel}>
                          Finansal Etki
                        </Text>
                        <Text style={styles.treatmentText}>
                          {disease.treatment_tr?.ekonomi ||
                            'Bilgi mevcut değil'}
                        </Text>
                      </View>
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
              <Text style={styles.resetButtonText}>🔄 Yeni Analiz</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Bottom Spacer */}
        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

// ─── Styles ──────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fafafa',
  },

  // Header
  header: {
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
    shadowColor: '#0f172a',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 3,
  },
  headerAccent: {
    height: 4,
    backgroundColor: '#7DA78C',
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
    fontSize: 22,
    fontWeight: '800',
    color: '#0f172a',
    letterSpacing: -0.3,
  },
  headerSubtitle: {
    fontSize: 13,
    color: '#64748b',
    marginTop: 2,
  },
  logoutButton: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#f8f9fa',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  logoutIcon: {
    fontSize: 18,
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
    backgroundColor: '#22c55e',
    marginRight: 8,
  },
  greetingText: {
    fontSize: 13,
    color: '#64748b',
  },
  greetingName: {
    fontWeight: '700',
    color: '#334155',
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
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    shadowColor: '#0f172a',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 12,
  },

  // Photo Area
  photoArea: {
    height: 300,
    borderRadius: 14,
    overflow: 'hidden',
    backgroundColor: '#f8faf8',
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
    borderColor: '#d4e6da',
    borderStyle: 'dashed',
    borderRadius: 14,
  },
  placeholderIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  placeholderText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#64748b',
    marginBottom: 4,
  },
  placeholderHint: {
    fontSize: 12,
    color: '#94a3b8',
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
    borderRadius: 14,
    gap: 8,
    shadowColor: '#0f172a',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 6,
    elevation: 2,
  },
  cameraButton: {
    backgroundColor: '#ffffff',
    borderWidth: 1.5,
    borderColor: '#7DA78C',
  },
  galleryButton: {
    backgroundColor: '#ffffff',
    borderWidth: 1.5,
    borderColor: '#7DA78C',
  },
  actionButtonIcon: {
    fontSize: 20,
  },
  actionButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#7DA78C',
  },

  // Analyze Button
  analyzeButton: {
    backgroundColor: '#7DA78C',
    height: 54,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#7DA78C',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 5,
  },
  analyzeButtonDisabled: {
    backgroundColor: '#bcc8c1',
    shadowOpacity: 0,
    elevation: 0,
  },
  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  analyzeButtonText: {
    fontSize: 17,
    fontWeight: '800',
    color: '#ffffff',
    letterSpacing: 0.3,
  },

  // Error
  errorCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fef2f2',
    borderRadius: 14,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#fecaca',
  },
  errorIcon: {
    fontSize: 18,
    marginRight: 10,
  },
  errorText: {
    flex: 1,
    fontSize: 13,
    color: '#dc2626',
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
    backgroundColor: '#e5e7eb',
  },
  dividerText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#334155',
  },

  // Result Card
  resultCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 18,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    shadowColor: '#0f172a',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 2,
  },
  resultCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
    gap: 8,
  },
  resultCardIcon: {
    fontSize: 20,
  },
  resultCardTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#334155',
  },

  // Plant Chips
  plantChipsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  plantChip: {
    backgroundColor: '#f0fdf4',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#bbf7d0',
  },
  plantChipText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#16a34a',
  },
  noDataText: {
    fontSize: 13,
    color: '#94a3b8',
    fontStyle: 'italic',
  },

  // Health Badge
  healthBadge: {
    borderRadius: 14,
    paddingHorizontal: 18,
    paddingVertical: 12,
    alignItems: 'center',
    borderWidth: 1,
  },
  healthBadgeText: {
    fontSize: 15,
    fontWeight: '700',
  },

  // Risk Score
  riskScoreContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    marginBottom: 14,
  },
  riskScoreValue: {
    fontSize: 42,
    fontWeight: '900',
    letterSpacing: -1,
  },
  riskLabel: {
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderWidth: 1,
  },
  riskLabelText: {
    fontSize: 13,
    fontWeight: '700',
  },
  riskBarBackground: {
    height: 8,
    backgroundColor: '#f1f5f9',
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
    borderBottomColor: '#f1f5f9',
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
    backgroundColor: '#7DA78C',
  },
  detectionName: {
    fontSize: 14,
    color: '#334155',
    fontWeight: '500',
    flex: 1,
  },
  confidenceBadge: {
    backgroundColor: '#f0f5f2',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  confidenceText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#7DA78C',
  },

  // Disease Section
  diseaseSectionHeader: {
    marginTop: 6,
    marginBottom: 12,
  },
  diseaseSectionTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0f172a',
  },

  // Disease Card
  diseaseCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 18,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderLeftWidth: 4,
    borderLeftColor: '#ef4444',
    shadowColor: '#0f172a',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
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
    backgroundColor: '#fef2f2',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#fecaca',
  },
  diseaseNumber: {
    fontSize: 14,
    fontWeight: '800',
    color: '#ef4444',
  },
  diseaseNameContainer: {
    flex: 1,
  },
  diseaseName: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
  },
  diseaseNameEn: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 2,
    fontStyle: 'italic',
  },

  // Treatment Items
  treatmentItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 14,
    gap: 12,
  },
  treatmentIconBox: {
    width: 38,
    height: 38,
    borderRadius: 10,
    backgroundColor: '#f0fdf4',
    justifyContent: 'center',
    alignItems: 'center',
  },
  treatmentIcon: {
    fontSize: 18,
  },
  treatmentContent: {
    flex: 1,
  },
  treatmentLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#64748b',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 3,
  },
  treatmentText: {
    fontSize: 14,
    color: '#334155',
    lineHeight: 20,
  },

  // Reset Button
  resetButton: {
    backgroundColor: '#ffffff',
    height: 52,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
    borderWidth: 2,
    borderColor: '#7DA78C',
  },
  resetButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#7DA78C',
  },
});
