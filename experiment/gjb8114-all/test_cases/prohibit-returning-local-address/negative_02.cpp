struct Point {
    int x;
    int y;
};

int* get_local_member_address() {
    Point point{1, 2};
    return &point.x; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-4]
}

int main() {
    int* p = get_local_member_address();
    (void)p;
    return 0;
}
