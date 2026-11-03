class Settings {
public:
    int limit;
    int Limit; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-8]
};

int main() {
    Settings s;
    s.limit = 1;
    s.Limit = 2;
    return s.limit + s.Limit;
}
