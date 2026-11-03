int main() {
    bool first = true;
    bool second = false;
    int count = 0;
    do {
        ++count;
    } while (first < second); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-1]
    return count;
}
