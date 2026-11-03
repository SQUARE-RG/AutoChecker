struct Point {
  int x;
  int y;
};

int getY(Point& p) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-2]
  return p.y;
}

int main() {
  Point pt{1, 2};
  return getY(pt);
}
