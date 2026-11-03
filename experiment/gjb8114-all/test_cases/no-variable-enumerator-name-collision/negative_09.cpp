enum Choice { yes, no };

int main() {
    switch (int no = 0; no) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-5]
    case 0:
        return 0;
    default:
        return 1;
    }
}
