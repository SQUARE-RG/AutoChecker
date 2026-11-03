struct Point {
  int x;
  int y;
};

int getX(Point* p) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-2]
  return p->x;
}

int main() {
  Point pt{1, 2};
  return getX(&pt);
}
