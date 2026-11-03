class MixedInit {
private:
    int a;
    int b;
    int c;
public:
    MixedInit(int v);
};

MixedInit::MixedInit(int v) : a(v) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-4]
    b = v;
}

int main() {
    MixedInit m(1);
    (void)m;
    return 0;
}
