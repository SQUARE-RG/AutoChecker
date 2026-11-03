typedef unsigned int Count;
int main() {
    unsigned int total = 0;
    for (unsigned int Count = 0; Count < 3; ++Count) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-6]
        total += Count;
    }
    return static_cast<int>(total);
}
