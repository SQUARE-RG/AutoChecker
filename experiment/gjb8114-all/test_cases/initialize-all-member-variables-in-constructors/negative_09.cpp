class EmptyInit {
private:
    int x;
    int y;
public:
    EmptyInit() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-4]
    }
};

int main() {
    EmptyInit e;
    (void)e;
    return 0;
}
