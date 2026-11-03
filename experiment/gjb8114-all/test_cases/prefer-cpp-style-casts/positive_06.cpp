enum class Color { Red = 1, Green = 2 };

Color intToColor(int value) {
  return static_cast<Color>(value);
}
