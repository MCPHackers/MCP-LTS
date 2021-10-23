import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import com.mojang.minecraft.Minecraft;

public final class GameWindowListener extends WindowAdapter {

   // $FF: synthetic field
   final Minecraft mc;
   // $FF: synthetic field
   final Thread thread;


   public GameWindowListener(Minecraft var1, Thread var2) {
      this.mc = var1;
      this.thread = var2;
   }

   public void windowClosing(WindowEvent var1) {
	  mc.running = false;
	  try {
         this.thread.join();
      } catch (Exception var3) {
         var3.printStackTrace();
      }

      System.exit(0);
   }
}
