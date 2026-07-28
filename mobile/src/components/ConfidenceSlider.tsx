// ─────────────────────────────────────────────────────────────────────
// Güven eşiği kaydırıcısı — app.py'deki st.slider(0.00–1.00, step 0.01)
// karşılığı. Parmakla sürüklenir; ray üzerine dokununca da o değere atlar.
// Ek bağımlılık gerektirmemesi için PanResponder ile elle yazıldı.
// ─────────────────────────────────────────────────────────────────────

import React, { useMemo, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  PanResponder,
  type LayoutChangeEvent,
} from 'react-native';
import { COLORS, FONTS } from '../constants/theme';

type Props = {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
};

const THUMB = 26;

export default function ConfidenceSlider({
  value,
  onChange,
  min = 0,
  max = 1,
  step = 0.01,
  disabled = false,
}: Props) {
  const [trackWidth, setTrackWidth] = useState(0);
  // Ray'in ekrandaki sol kenarı — sürükleme sırasında mutlak x'ten çıkarılır.
  const trackOriginX = useRef(0);
  const widthRef = useRef(0);
  const disabledRef = useRef(disabled);
  disabledRef.current = disabled;

  const clampToStep = (raw: number): number => {
    const clamped = Math.min(max, Math.max(min, raw));
    const stepped = Math.round((clamped - min) / step) * step + min;
    // Kayan nokta artıklarını temizle (0.30000000000000004 → 0.3)
    return Math.round(stepped * 1000) / 1000;
  };

  const emitFromX = (x: number) => {
    const width = widthRef.current;
    if (width <= 0) return;
    const ratio = x / width;
    onChange(clampToStep(min + ratio * (max - min)));
  };

  const panResponder = useMemo(
    () =>
      PanResponder.create({
        onStartShouldSetPanResponder: () => !disabledRef.current,
        onMoveShouldSetPanResponder: () => !disabledRef.current,
        // Sürükleme sırasında ScrollView'ın araya girip kaydırmasını engelle
        onPanResponderTerminationRequest: () => false,
        onPanResponderGrant: (evt) => {
          const { pageX, locationX } = evt.nativeEvent;
          trackOriginX.current = pageX - locationX;
          emitFromX(locationX);
        },
        onPanResponderMove: (evt) => {
          emitFromX(evt.nativeEvent.pageX - trackOriginX.current);
        },
      }),
    // onChange her render'da yeniden üretilmediği sürece tek kurulum yeterli
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const onLayout = (e: LayoutChangeEvent) => {
    const width = e.nativeEvent.layout.width;
    widthRef.current = width;
    setTrackWidth(width);
  };

  const ratio = max > min ? (value - min) / (max - min) : 0;
  const fillWidth = trackWidth * Math.min(1, Math.max(0, ratio));
  const thumbLeft = fillWidth - THUMB / 2;

  return (
    <View style={styles.wrapper}>
      {/* Dokunma alanı ray'den yüksek tutulur ki parmakla yakalaması kolay olsun */}
      <View
        style={[styles.touchArea, disabled && styles.disabled]}
        onLayout={onLayout}
        {...panResponder.panHandlers}
      >
        <View style={styles.track}>
          <View style={[styles.fill, { width: fillWidth }]} />
        </View>
        <View
          style={[
            styles.thumb,
            { left: Math.min(Math.max(thumbLeft, -THUMB / 2 + 2), trackWidth - THUMB / 2 - 2) },
          ]}
        >
          <View style={styles.thumbInner} />
        </View>
      </View>

      <View style={styles.scaleRow}>
        <Text style={styles.scaleText}>{min.toFixed(2)}</Text>
        <Text style={styles.scaleText}>{((min + max) / 2).toFixed(2)}</Text>
        <Text style={styles.scaleText}>{max.toFixed(2)}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    marginTop: 14,
  },
  touchArea: {
    height: THUMB + 8,
    justifyContent: 'center',
  },
  disabled: {
    opacity: 0.5,
  },
  track: {
    height: 8,
    borderRadius: 4,
    backgroundColor: COLORS.borderSoft,
    borderWidth: 1,
    borderColor: COLORS.border,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    backgroundColor: COLORS.primary,
  },
  thumb: {
    position: 'absolute',
    width: THUMB,
    height: THUMB,
    borderRadius: THUMB / 2,
    backgroundColor: COLORS.white,
    borderWidth: 2,
    borderColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#0f172a',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 4,
  },
  thumbInner: {
    width: 9,
    height: 9,
    borderRadius: 5,
    backgroundColor: COLORS.primary,
  },
  scaleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 2,
  },
  scaleText: {
    fontFamily: FONTS.medium,
    fontSize: 11,
    color: COLORS.textMuted,
  },
});
