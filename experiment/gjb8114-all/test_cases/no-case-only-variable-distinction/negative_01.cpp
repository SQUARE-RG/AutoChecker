int main() {
    int fSpeed = 1;
    int fspeed = 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-8]
    return fSpeed + fspeed;
}
