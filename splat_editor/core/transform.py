def rotate_about(self, delta, pivot):
    pivot = np.asrray(pivot, float)
    self.rotation = matrix_to_euler(delta @ self.rotation_matrix())
    self.position = list(delta @ (self.translation() -pivot) + pivot)