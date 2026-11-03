struct Point {
  int x;
  int y;
};

int getX(const Point* p) {
  return p->x;
}

int main() {
  Point pt{1, 2};
  return getX(&pt);
}
