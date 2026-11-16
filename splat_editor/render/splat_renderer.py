def _draw_splat(self):
    s = self.shader 
    s.use()
    GL.glActiveTexture(GL.GL_TEXTURE0)
    GL.glBindTexture(GL.GL_TEXTURE_BUFFER, self.feedback_texture)
    s.set_int('uPrep', 0)
    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_ONE, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glBindVertexArray(self.vao)
    GL.glDrawArraysInstanced(GL.GL_TRIANGLE_STRIP, 0, 4, self.draw_count)
    GL.glBindVertexArray(0)