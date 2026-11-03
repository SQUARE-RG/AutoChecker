int main() {
    bool left = true;
    bool right = false;
    bool greater = left > right; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-1]
    return greater ? 0 : 1;
}
