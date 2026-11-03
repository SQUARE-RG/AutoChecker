struct Point {
  int x;
  int y;
};

int getY(const Point& p) {
  return p.y;
}

int main() {
  Point pt{1, 2};
  return getY(pt);
}
