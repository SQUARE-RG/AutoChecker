int main() {
    unsigned int mask = 0777; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-4]
    return static_cast<int>(mask);
}
