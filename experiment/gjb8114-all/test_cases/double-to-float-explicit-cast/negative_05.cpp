struct FloatHolder {
    float value;
};

int main() {
    double dValue = 0.0;
    FloatHolder holder;
    holder.value = dValue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-3]
    return 0;
}
