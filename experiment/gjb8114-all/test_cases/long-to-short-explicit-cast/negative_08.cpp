int main() {
    unsigned long wideValue = 300UL;
    unsigned char narrowValue = 0;
    narrowValue = wideValue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-2]
    return static_cast<int>(narrowValue);
}
