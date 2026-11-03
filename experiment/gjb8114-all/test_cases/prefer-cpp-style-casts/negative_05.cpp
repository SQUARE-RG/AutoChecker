enum class Color { Red = 1, Green = 2 };

int colorToInt(Color c) {
  return (int)c; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-5-1]
}
