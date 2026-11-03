int main() {
    int score = 100;
    {
        int score = 50; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-7]
        score += 10;
    }
    return score;
}
