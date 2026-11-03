int GlobalCount = 0;
int globalCount = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-8]

int main() {
    return GlobalCount + globalCount;
}
