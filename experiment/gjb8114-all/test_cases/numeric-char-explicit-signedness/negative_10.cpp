struct Flags {
    char level : 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-20]
    int score;
};

int main() {
    Flags f;
    f.level = 2;
    f.score = f.level + 1;
    return f.score;
}
