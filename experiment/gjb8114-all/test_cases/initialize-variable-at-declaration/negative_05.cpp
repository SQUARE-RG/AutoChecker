int main() {
  int value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-1]
  for (value = 0; value < 4; ++value) {
    if (value == 2) {
      break;
    }
  }
  return value;
}
