int g_lookup_table[4] = {1, 2, 3, 4}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-2]

int main() {
    int sum = 0;
    for (int value : g_lookup_table) {
        sum += value;
    }
    return sum == 10 ? 0 : 1;
}
