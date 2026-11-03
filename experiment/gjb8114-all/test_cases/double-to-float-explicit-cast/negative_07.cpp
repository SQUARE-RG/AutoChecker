struct DHolder {
    double value;
};

int main() {
    DHolder holder;
    holder.value = 0.0;
    float fData;
    fData = holder.value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-3]
    return 0;
}
