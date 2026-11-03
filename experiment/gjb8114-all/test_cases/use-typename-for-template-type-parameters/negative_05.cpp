struct Calculator {
  template<class T> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-1]
  T plus(T left, T right) {
    return left + right;
  }
};

int main() {
  Calculator calculator;
  return calculator.plus(1, 2);
}
