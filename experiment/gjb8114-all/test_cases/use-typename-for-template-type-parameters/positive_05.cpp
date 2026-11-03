struct Calculator {
  template<typename T>
  T plus(T left, T right) {
    return left + right;
  }
};

int main() {
  Calculator calculator;
  return calculator.plus(1, 2);
}
