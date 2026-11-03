int main() {
    struct LocalReporter {
        int used_path() const {
            return 1;
        }

        int orphaned_path() const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-3]
            return 2;
        }
    };

    LocalReporter reporter;
    return reporter.used_path();
}
