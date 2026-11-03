enum class Color { Red = 1, Green = 2 };

Color intToColor(int value) {
  return Color(value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-5-1]
}
