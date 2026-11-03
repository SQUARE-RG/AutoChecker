struct Point {
    int x;
    int y;
};

Point operator+(const Point& lhs, const Point& rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-2]
    return lhs;
}

int main() {
    Point p{1, 2};
    Point q{3, 4};
    auto r = p + q;
    (void)r;
    return 0;
}
