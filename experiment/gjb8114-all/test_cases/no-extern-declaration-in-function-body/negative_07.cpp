int global_value = 0;

int main() {
    auto read_global = []() {
        extern int global_value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-17]
        return global_value;
    };
    return read_global();
}
