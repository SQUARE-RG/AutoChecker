struct S {
    int i;
    int j;
    int k;
};

class C {
public:
    C() : i(0) {}
    virtual ~C() {}
    int i;
};

int main() {
    S* s = new S{1, 2, 3};
    C* c = reinterpret_cast<C*>(s); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-1]
    (void)c;
    delete s;
    return 0;
}
