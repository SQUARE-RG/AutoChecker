// negative_05.cpp
void processValues() {
    unsigned short values[4] = {1, 2, 3, 4}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-1]
    (void)values;
}
