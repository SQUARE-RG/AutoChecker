struct FloatHolder {
    float value;
};

int main() {
    double dValue = 0.0;
    FloatHolder holder;
    holder.value = static_cast<float>(dValue);
    return 0;
}
