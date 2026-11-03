struct DHolder {
    double value;
};

int main() {
    DHolder holder;
    holder.value = 0.0;
    float fData;
    fData = static_cast<float>(holder.value);
    return 0;
}
