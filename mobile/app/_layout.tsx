import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { View, ActivityIndicator } from 'react-native';
import {
  useFonts,
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  Inter_700Bold,
  Inter_800ExtraBold,
  Inter_900Black,
} from '@expo-google-fonts/inter';
import { COLORS } from '../src/constants/theme';
import { LanguageProvider } from '../src/context/LanguageContext';

export default function RootLayout() {
  const [fontsLoaded] = useFonts({
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    Inter_700Bold,
    Inter_800ExtraBold,
    Inter_900Black,
  });

  // Fontlar yüklenene kadar sade bir yükleniyor ekranı göster.
  // (Sistem fontu kullanır; Inter'e HENÜZ referans verilmez ki Android'de
  // "font not loaded" hatası oluşmasın.)
  if (!fontsLoaded) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: COLORS.primarySoft,
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <LanguageProvider>
      {/* Koyu yeşil başlık / fotoğraflı giriş ekranı üzerinde açık renk ikonlar */}
      <StatusBar style="light" backgroundColor={COLORS.darkGreen} />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: COLORS.bgPage },
          animation: 'slide_from_right',
        }}
      >
        <Stack.Screen name="index" />
        <Stack.Screen name="home" />
        <Stack.Screen name="history" />
      </Stack>
    </LanguageProvider>
  );
}
