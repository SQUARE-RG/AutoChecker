template <typename T>
int adjust_value(T value) {
  int result = static_cast<int>(value);
  if (result > 10) {
    result -= 1;
  }
  for (int i = 0; i < 2; ++i) {
    result += i;
  }
  return result;
}
