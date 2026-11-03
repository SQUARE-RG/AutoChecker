int main() {
    int chosenValue = 1, chosenvalue = 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-8]
    return chosenValue + chosenvalue;
}
