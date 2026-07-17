import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <>
      <StatusBar style="dark" backgroundColor="#f0f5f2" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: '#fafafa' },
          animation: 'slide_from_right',
        }}
      >
        <Stack.Screen name="index" />
        <Stack.Screen name="home" />
      </Stack>
    </>
  );
}
