struct Number {
  int value;
};

Number operator+(const Number& lhs, const Number& rhs) {
  Number result;
  result.value = lhs.value + rhs.value;
  return result;
}
